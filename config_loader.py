import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def load_config(filename: str, section: str):
    with open(filename) as c:
        config = yaml.load(c, Loader)
        return config.get(section, None)
