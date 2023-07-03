import yaml

if hasattr(yaml, 'CSafeLoader'):
    # make a dynamic subclass so we don't override global yaml Loader
    yaml_loader = type('CustomLoader', (yaml.CSafeLoader,), {})
else:
    yaml_loader = type('CustomLoader', (yaml.SafeLoader,), {})


def yaml_load(tmpl_str):
    return yaml.load(tmpl_str, Loader=yaml_loader)


def read_yaml_file(path):
    """Read yaml file"""
    with open(path) as stream:
        data = yaml_load(stream)
        return data
