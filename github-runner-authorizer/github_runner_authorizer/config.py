from everett.component import RequiredConfigMixin, ConfigOptions
from everett.manager import ConfigManager, ConfigOSEnv


class BotConfig(RequiredConfigMixin):
    required_config = ConfigOptions()
    required_config.add_option('app_id', parser=str, doc='The app ID of the GitHub app.')
    required_config.add_option('installation_id', parser=str, doc='The installation ID to get access tokens for.')
    required_config.add_option('namespace', parser=str, doc='The Kubernetes namespace this script is running in.')
    required_config.add_option('private_key', parser=str, doc='The private key of the GitHub app.')


def get_config():
    config = ConfigManager(environments=[
        ConfigOSEnv()
    ])
    return config.with_options(BotConfig())
