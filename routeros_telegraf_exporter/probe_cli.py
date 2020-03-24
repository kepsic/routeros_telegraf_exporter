"""Console script for routeros_telegraf_exporter.

This module is for rte_probe console script entry point.

Example:

    $ rte_probe --host router1.example.com --path /system/resource
"""
import argparse
import logging
import os

import routeros_api

logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    datefmt='%m-%d %H:%M',
                    filemode='w')


def main():
    """Main probe function
    Returns:
    int: 0 if ok, 100 if fail
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", dest="user", default=os.getenv("ROUTEROS_API_USERNAME", 'api_read_user'))
    parser.add_argument("-p", "--password", dest="password",
                        default=os.getenv("ROUTEROS_API_PASSWORD", 'do_not_expose_password_here'))
    parser.add_argument("-P", "--port", dest="port", type=int, default=os.getenv("ROUTEROS_API_PORT", 8728))
    parser.add_argument("-H", "--host", required=True, dest="host")
    parser.add_argument("--path", required=True, dest="path")
    args = parser.parse_args()
    try:
        api = routeros_api.RouterOsApiPool(args.host,
                                           port=args.port,
                                           username=args.user,
                                           password=args.password,
                                           plaintext_login=True).get_api()
        for address in api.get_resource(args.path).get():
            logging.info(address)
    except Exception as e:
        logging.error(e)
        return 100
    return 0

if __name__ == "__main__":
    pass  # pragma: no cover
