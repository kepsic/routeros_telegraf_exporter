"""Console script for routeros_telegraf_exporter."""
import argparse
import os
import sys

from threading import Thread

from queue import Queue

from .models import load_hosts_config
from .routeros_exporter import worker


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", dest="user", default=os.getenv("ROUTEROS_API_USERNAME", 'api_read_user'))
    parser.add_argument("-p", "--password", dest="password",
                        default=os.getenv("ROUTEROS_API_PASSWORD", 'do_not_expose_password_here'))
    parser.add_argument("-P", "--port", dest="port", type=int, default=os.getenv("ROUTEROS_API_PORT", 8728))
    parser.add_argument("-H", "--hosts", dest="hosts", default=os.getenv("ROUTEROS_EXPORTER_HOSTS"))
    parser.add_argument("-D", dest="daemon", action="store_true")
    parser.add_argument("--output-type", dest="output", choices=("influx", "json"), default="influx")
    parser.add_argument("--hosts-config-file", dest="hosts_config_file")
    return parser.parse_args()


def main(args=parse_args()):
    q = Queue()
    qworker = Thread(target=worker, args=(args, q,))
    qworker.setDaemon(True)
    qworker.start()
    if args.hosts_config_file:
        args.hosts_config = load_hosts_config(args.hosts_config_file)

    print_values(args, q)

    while args.daemon:
        print_values(args, q)

    return 0


def print_values(args, q):
    values = []
    while not q.empty():
        values.append(q.get())
    if args.output == "influx":
        if values:
            v = []
            for x in values:
                for x2 in x:
                    v.append(x2)
            print("\n".join(v))
    elif args.output == "json":
        import json
        print(json.dumps(values))


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
