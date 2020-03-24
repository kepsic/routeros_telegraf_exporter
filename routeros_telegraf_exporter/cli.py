"""Console script for routeros_telegraf_exporter.

This module is for rte console script entry point.

Examples:
    Run in in interactive (ignores resource interval) mode::

        $ rte --hosts-config-file hosts_config.yaml -i

    Run in in daemon mode::

        $ rte --hosts-config-file hosts_config.yaml -D
"""
import argparse
import logging
import os


from threading import Thread

from queue import Queue

from .utils import format_values_to_str
from .models import load_config, load_hosts_from_config
from .routeros_exporter import worker


def configure_logging(args):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=args.logfile,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)


def start_thread(args):
    q = Queue()
    qworker = Thread(target=worker, args=(args, q, args.daemon))
    qworker.setDaemon(args.daemon)
    qworker.start()
    return q


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", dest="user", default=os.getenv("ROUTEROS_API_USERNAME", 'api_read_user'))
    parser.add_argument("-p", "--password", dest="password",
                        default=os.getenv("ROUTEROS_API_PASSWORD", 'do_not_expose_password_here'))
    parser.add_argument("-P", "--port", dest="port", type=int, default=os.getenv("ROUTEROS_API_PORT", 8728))
    parser.add_argument("-H", "--hosts", dest="hosts", default=os.getenv("ROUTEROS_EXPORTER_HOSTS"))
    parser.add_argument("-D", dest="daemon", action="store_true", default=False)
    parser.add_argument("-i", "--ignore-interval", dest="ignore_interval", action="store_true", default=False)
    parser.add_argument("--output-type", dest="output_type", choices=("influx", "json"), default="influx")
    parser.add_argument("--hosts-config-file", dest="hosts_config_file")
    parser.add_argument("-l", "--logfile", dest="logfile", default="/tmp/routeros_telegraf_exporter.log")

    return parser.parse_args()


def cli_main(args=parse_args()):
    configure_logging(args)
    if args.hosts_config_file:
        args.hosts_config = load_config(args.hosts_config_file)
        args.hosts = load_hosts_from_config(args.hosts_config)

    if args.daemon:
        q = start_thread(args)
    else:
        q = Queue()
        values = worker(args, q, False)
        for value in values:
            for v in value:
                q.put(v)
                print_values(args, q)

    while args.daemon:
        print_values(args, q)
    return 0


def print_values(args, q):
    values = []
    while not q.empty():
        values.append(q.get())
    if args.output_type == "influx":
        if values:
            logging.info(format_values_to_str(values))
    elif args.output_type == "json":
        logging.info(values)

if __name__ == "__main__":
    pass  # pragma: no cover
