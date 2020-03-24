import re


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
