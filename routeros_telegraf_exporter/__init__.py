"""Main entry point
"""
import os
import re

from pyramid.config import Configurator

DEFAULT_VALUES_FIELDS = "state"
DEFAULT_TAGS_FIELDS = "name"
DEFAULT_MEASUREMNT = "routerstat"
CONNECTIONS = {}


def format_values_to_str(values):
    v = []
    for x in values:
        for x2 in x:
            v.append(x2)
    return "\n".join(v)

def format_value(value_str):
    if re.match(r'^[-+]?([0-9]*\.[0-9]+)$', value_str):
        return float(value_str)
    elif re.match(r'^\d+$', value_str):
        return "{}i".format(value_str)


def format_tag(value_str):
    value_str = value_str.replace("*", "x").replace(" ", "_").replace(",", "_")
    return "{}".format(value_str)


def main(global_config, **settings):
    for key, value in settings.items():
        if re.match("^routeros_exporter.*", key):
            settings[key] = value
            os.environ[key.upper()] = value

    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("routeros_telegraf_exporter.views")
    return config.make_wsgi_app()
