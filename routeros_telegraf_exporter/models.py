"""Models module

Abstraction layer for models
"""

import os
import threading
from datetime import datetime

import yaml
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def load_config(config_file):
    here = os.path.abspath(os.path.dirname(__file__))
    config_file = "{}/{}".format(os.environ.get("ROUTEROS_EXPORTER_PATH", here), config_file)
    try:
        with open(config_file) as file:
            data = load(file, Loader=Loader)
            return data
    except FileNotFoundError:
        from routeros_telegraf_exporter import DEFAULT_CONF
        return load(DEFAULT_CONF, Loader=Loader)


def load_hosts_from_config(config):
    hosts = list(map(lambda x: list(x.keys())[0], config))
    if "default" in hosts:
        hosts.remove("default")
        return ",".join(hosts)


class Args(object):
    user = None
    host = None
    password = None
    port = 8728
    hosts = []
    sleep = 60
    resource = []
    ignore_interval = False

    def __init__(self, user=os.getenv("ROUTEROS_API_USERNAME", 'api_read_user'),
                 password=os.getenv("ROUTEROS_API_PASSWORD", 'do_not_expose_password_here'),
                 port=os.getenv("ROUTEROS_API_PORT", 8728),
                 hosts=[],
                 daemon=False,
                 output_type="influx",
                 resource=[],
                 hosts_config_file=os.getenv("ROUTEROS_EXPORTER_HOSTS_CONFIG", 'hosts_config.yaml'),
                 ignore_interval=False):
        self.lock = threading.Lock()
        self.user = user
        self.password = password
        self.hosts = hosts
        self.port = port
        self.daemon = daemon
        self.output_type = output_type
        self.resource = resource
        self.ignore_interval = ignore_interval
        self.hosts_config = load_config(hosts_config_file)
        if self.hosts_config:
            self.hosts = load_hosts_from_config(self.hosts_config)

class JsonData(object):
    time = None
    tags = dict([])
    fields = dict([])
    measuremenst = None

    def __init__(self, tags=dict([]), fields=dict([]), measurement=None):
        date = datetime.now()
        self.time = date.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.tags = tags
        self.fields = fields
