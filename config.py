import os
from configparser import ConfigParser


def load_config(filename='config.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(os.path.join(os.path.dirname(__file__), filename))

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config
