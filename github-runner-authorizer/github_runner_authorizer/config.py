from everett.component import RequiredConfigMixin, ConfigOptions
from everett.manager import ConfigManager, ConfigOSEnv


class BotConfig(RequiredConfigMixin):
    required_config = ConfigOptions()


def get_config():
    config = ConfigManager(environments=[
        ConfigOSEnv()
    ])
    return config.with_options(BotConfig())
