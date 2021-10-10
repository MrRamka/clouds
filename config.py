import configparser


def get_config_variables(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config
