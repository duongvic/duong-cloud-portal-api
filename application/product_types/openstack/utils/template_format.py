from __future__ import absolute_import

import yaml
from oslo_serialization import jsonutils

if hasattr(yaml, 'CSafeLoader'):
    # make a dynamic subclass so we don't override global yaml Loader
    yaml_loader = type('HeatYamlLoader', (yaml.CSafeLoader,), {})
else:
    yaml_loader = type('HeatYamlLoader', (yaml.SafeLoader,), {})

if hasattr(yaml, 'CSafeDumper'):
    yaml_dumper = yaml.CSafeDumper
else:
    yaml_dumper = yaml.SafeDumper


def _construct_yaml_str(self, node):
    # Override the default string handling function
    # to always return unicode objects
    return self.construct_scalar(node)


yaml_loader.add_constructor(u'tag:yaml.org,2002:str', _construct_yaml_str)


yaml_loader.add_constructor(u'tag:yaml.org,2002:timestamp', _construct_yaml_str)


def parse(tmpl_str):
    """
    Takes a string and returns a dict containing the parsed structure.
    This includes determination of whether the string is using the
    JSON or YAML format.
    :param tmpl_str:
    :return:
    """
    if tmpl_str.startswith('{'):
        tpl = jsonutils.loads(tmpl_str)
    else:
        try:
            # we already use SafeLoader when constructing special Heat YAML loader class
            tpl = yaml.load(tmpl_str, Loader=yaml_loader)
        except yaml.YAMLError as yea:
            raise ValueError(yea)
        else:
            if tpl is None:
                tpl = {}
    # Looking for supported version keys in the loaded template
    if not ('HeatTemplateFormatVersion' in tpl or
            'heat_template_version' in tpl or
            'AWSTemplateFormatVersion' in tpl):
        raise ValueError("Template format version not found.")
    return tpl
