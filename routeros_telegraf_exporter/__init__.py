"""Main entry point
"""

__author__ = """Andres Kepler"""
__email__ = 'andres@kepler.ee'
__version__ = '0.1.11'

import os
import re

from pyramid.config import Configurator

DEFAULT_VALUES_FIELDS = "state"
DEFAULT_TAGS_FIELDS = "name"
DEFAULT_MEASUREMNT = "routerstat"
CONNECTIONS = {}
DEFAULT_CONF = """
- default:
      resources:
          - path: /system/resource
            interval: 30
            tags:
                  - board-name
                  - disabled
            values:
                  - cpu-load
- rte_default_gw:
      resources:
          - path: /interface/ethernet
            interval: 15
            tags:
                - name
                - speed
                - disabled
            values:
                - rx-bytes
                - tx-bytes
"""


def main(global_config, **settings):
    for key, value in settings.items():
        if re.match("^routeros_exporter.*", key):
            settings[key] = value
            os.environ[key.upper()] = value

    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("routeros_telegraf_exporter.views")
    return config.make_wsgi_app()
