""" Main RouterOS API aggregator

This module is used to aggregate RouterOS API values into influx line protocol or JSON
"""
import logging
import os
import time

import routeros_api

from routeros_telegraf_exporter import DEFAULT_MEASUREMNT, CONNECTIONS
from routeros_telegraf_exporter.utils import format_value, format_tag
from routeros_telegraf_exporter.models import JsonData

MEASUREMENT = os.environ.get("ROUTEROS_EXPORTER_MEASUREMENT", DEFAULT_MEASUREMNT)
EXPORT_OUTPUT_LINE = MEASUREMENT + ",{} {} {}"
last_resouce_run_dict = {}

log = logging.getLogger(__name__)


def host_output(args):
    """Aggregates RouterOS-API path into list

    Args:
        args (object): Parameters object

    Returns:
        list: Multidimensional aggregated list
    """
    api = CONNECTIONS.get(args.host)
    if not api:
        return
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
                    value = transform_dict.get(value, default_value)
                    extra_values.append((name, value))

        if extra_values and tag_values:
            if args.output_type == "json":
                res.append(JsonData(measurement=MEASUREMENT, tags=dict(tag_values), fields=dict(extra_values)).__dict__)
            elif args.output_type == "influx":
                res.append(
                    EXPORT_OUTPUT_LINE.format(','.join(list(map(lambda x: "{v[0]}={v[1]}".format(v=x), tag_values))),
                                              ','.join(list(map(lambda x: "{v[0]}={v[1]}".format(v=x), extra_values))),
                                              time.time_ns())
                )

    return res


def extract_default_resouces(args):
    """Helper function to extracts default resources from config file
    Args:
    args (object): Arguments object
    Returns:
    dict: Default section from config or None

    """
    res = list(filter(lambda x: x.get("default"), args.hosts_config))
    if res:
        return res[0]['default']['resources']
    return None


def close_connections():
    """Helper function for closing routeros connections
    """
    for srv, connection in CONNECTIONS.items():
        connection.disconnect()


def get_connections(args):
    """Helper function for building connection pool for routers

    Args:
        args (object): Arguments object
    """
    if not args.hosts:
        raise RuntimeError("Missing hosts param")
    hosts = args.hosts.split(",")
    for host in hosts:
        if host == "rte_default_gw":
            return
        args.host = host
        connection = CONNECTIONS.get(args.host)
        if not connection:
            try:
                CONNECTIONS[args.host] = routeros_api.RouterOsApiPool(args.host,
                                                                  port=args.port,
                                                                  username=args.user,
                                                                  password=args.password,
                                                                  plaintext_login=True).get_api()
            except routeros_api.exceptions.RouterOsApiConnectionError as e:
                logging.error("Unable to connect {}: {}".format(args.host, e))
                pass



def get_routers_data(args, hosts, q):
    """Iterates over hosts and returns aggregated values

    Args:
        args (object): Parameters object
        hosts (str): Comma separated hosts
        q (Queue): Queue object

    Returns:
        list: List of agregated routers values
    """
    routers_values = []
    for host in hosts:
        router_value = get_router_data(args, host, q)
        routers_values.append(router_value)
    return routers_values


def get_router_data(args, host, q):
    """Main RouterOS-API values aggregator

    Args:
        args (object): Arguments object
        host (str): Host string
        q (Queue): Queue object

    Returns:
        list: Agregated list of values

    """
    global last_resouce_run_dict
    router_values = []
    host_config = list(filter(lambda x: x.get(host), args.hosts_config))
    if not host_config:
        return
    default_config_resources = extract_default_resouces(args)
    host_config = host_config[0].get(host)
    resources = host_config.get('resources')
    if default_config_resources:
        resources.extend(default_config_resources)
    for resource in resources:
        args.host = host
        args.resource = resource
        if not args.ignore_interval and not args.daemon:
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
            last_resouce_run_dict[last_resource_run_key] = current_milli_sec
        values = host_output(args)
        if not q.full():
            q.put(values)
        router_values.append(values)
    return router_values


def worker(args, q, daemon=True):
    """Main worker for cli and web application

    Args:
        args (object): Arguments object
        q (Queue): Queue object where the results is stored
        daemon (bool): On True iterates endlessly

    Returns:
        list: Multidimensional list of agregated values

    """
    get_connections(args)
    hosts = args.hosts.split(",")
    values = []
    if not daemon:
        values = get_routers_data(args, hosts, q)
    while daemon:
        values = get_routers_data(args, hosts, q)
    return values
