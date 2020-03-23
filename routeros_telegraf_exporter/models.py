import os
import threading
from datetime import datetime
from yaml import load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def load_hosts_config(config_file):
    here = os.path.abspath(os.path.dirname(__file__))
    config_file = "{}/{}".format(os.environ.get("ROUTEROS_EXPORTER_PATH", here), config_file)
    with open(config_file) as file:
        data = load(file, Loader=Loader)
        return data


class Args(object):
    user = None
    host = None
    password = None
    port = 8728
    hosts = []
    sleep = 60
    resource = []

    def __init__(self, user=os.getenv("ROUTEROS_API_USERNAME", 'api_read_user'),
                 password=os.getenv("ROUTEROS_API_PASSWORD", 'do_not_expose_password_here'),
                 port=os.getenv("ROUTEROS_API_PORT", 8728),
                 hosts=[],
                 daemon=False,
                 output="influx",
                 resource=[],
                 hosts_config_file=os.getenv("ROUTEROS_EXPORTER_HOSTS_CONFIG", 'hosts_config.yaml')):
        self.lock = threading.Lock()
        self.user = user
        self.password = password
        self.hosts = hosts
        self.port = port
        self.daemon = daemon
        self.output = output
        self.resource = resource
        self.hosts_config = load_hosts_config(hosts_config_file)

    def load_hosts_from_config(self):
        hosts = list(map(lambda x: list(x.keys())[0], self.hosts_config))
        if "default" in hosts:
            hosts.remove("default")
            self.hosts = ",".join(hosts)


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
