# TODO it is unclear whether doing it manually (like this)
# is better or worse than hacking extra options into plover's config class
section = "Console UI"


def get(config, option):
    if config._config.has_section(section):
        if config._config[section][option]:
            return config._config[section][option]
    return None


def set(config, option, value):
    if not config._config.has_section(section):
        config._config.add_section(section)
    config._config.set(section, option, value)
