import os
import time

import routeros_api

from routeros_telegraf_exporter import DEFAULT_MEASUREMNT, CONNECTIONS, \
    format_value, format_tag
from routeros_telegraf_exporter.models import JsonData

MEASUREMENT = os.environ.get("ROUTEROS_EXPORTER_MEASUREMENT", DEFAULT_MEASUREMNT)
EXPORT_OUTPUT_LINE = MEASUREMENT + ",{} {} {}"
last_resouce_run_dict = {}


def host_output(args):
    api = CONNECTIONS.get(args.host)
    list_adress = api.get_resource(args.resource.get("path"))
    res = []
    tags_fields = args.resource.get("tags")
    values_fields = args.resource.get("values")
    values_transform = args.resource.get("values_transform")

    for address in list_adress.get():
        extra_values = []
        tag_values = [("router_name", args.host)]

        # If value key is missing from address
        for value_field in values_fields:
            if value_field not in address.keys() and values_transform:
                transform_values = list(filter(lambda x: x.get(value_field), values_transform))
                if transform_values:
                    address[value_field] = "missing"

        for key, value in address.items():
            # Tags
            if format_tag(value) and key in tags_fields:
                tag_values.append((key, format_tag(value)))

            # Values
            if format_value(value) and key in values_fields:
                extra_values.append((key, format_value(value)))

            # Transform values
            if values_transform:
                transform_values = list(filter(lambda x: x.get(key), values_transform))
                if transform_values:
                    transform_dict = transform_values[0].get(key)
                    default_value = transform_dict.get("default")
                    name = transform_dict.get("rename", key)
                    extra_values.append((name, transform_dict.get(value, default_value)))

        if extra_values and tag_values:
            if args.output == "json":
                res.append(JsonData(measurement=MEASUREMENT, tags=dict(tag_values), fields=dict(extra_values)).__dict__)
            elif args.output == "influx":
                res.append(
                    EXPORT_OUTPUT_LINE.format(','.join(list(map(lambda x: "{v[0]}={v[1]}".format(v=x), tag_values))),
                                              ','.join(list(map(lambda x: "{v[0]}={v[1]}".format(v=x), extra_values))),
                                              time.time_ns())
                )

    return res


def extract_default_resouces(args):
    res = list(filter(lambda x: x.get("default"), args.hosts_config))
    if res:
        return res[0]['default']['resources']
    return None


def close_connections():
    for srv, connection in CONNECTIONS.items():
        connection.disconnect()


def get_connections(args):
    hosts = args.hosts.split(",")
    for host in hosts:
        args.host = host
        connection = CONNECTIONS.get(args.host)
        if not connection:
            CONNECTIONS[args.host] = routeros_api.RouterOsApiPool(args.host,
                                                                  port=args.port,
                                                                  username=args.user,
                                                                  password=args.password,
                                                                  plaintext_login=True).get_api()


def get_routers_data(args, hosts, q, values):
    for host in hosts:
        get_router_data(args, host, q, values)
    return values


def get_router_data(args, host, q, values):
    global last_resouce_run_dict
    host_config = list(filter(lambda x: x.get(host), args.hosts_config))
    default_config_resources = extract_default_resouces(args)
    host_config = host_config[0][host]
    resources = host_config.get('resources')
    if default_config_resources:
        resources.extend(default_config_resources)
    for resource in resources:
        args.host = host
        args.resource = resource
        resource_path = resource.get("path")
        resource_interval_millis = resource.get("interval", 60) * 1000
        last_resource_run_key = "{}_{}".format(host.replace(".", "_"), resource_path.replace("/", "_"))
        current_milli_sec = int(round(time.time() * 1000))
        last_resouce_run_millis = last_resouce_run_dict.get(last_resource_run_key)
        if not last_resouce_run_millis:
            last_resouce_run_dict[last_resource_run_key] = current_milli_sec
            last_resouce_run_millis = current_milli_sec
        if (current_milli_sec - last_resouce_run_millis) < resource_interval_millis:
            continue
        print("Exec", last_resource_run_key, current_milli_sec, last_resouce_run_millis, resource_interval_millis)
        values = host_output(args)
        if not q.full():
            last_resouce_run_dict[last_resource_run_key] = current_milli_sec
            q.put(values)
    return values


def worker(args, q, sleep=True):
    get_connections(args)
    hosts = args.hosts.split(",")
    values = []
    if not sleep:
        values = get_routers_data(args, hosts, q, values)
    while sleep:
        values = get_routers_data(args, hosts, q, values)
    return values
