from everett.component import RequiredConfigMixin, ConfigOptions
from everett.manager import ConfigManager, ConfigOSEnv


class BotConfig(RequiredConfigMixin):
    required_config = ConfigOptions()
    required_config.add_option('github_owner', parser=str, default='longhorn', doc='Set the owner of the target GitHub '
                                                                                   'repository.')
    required_config.add_option('github_repository', parser=str, default='longhorn', doc='Set the name of the target '
                                                                                        'GitHub repository.')
    required_config.add_option('github_token', parser=str, doc='Set the token of the GitHub machine user.')
    required_config.add_option('zenhub_pipeline', parser=str, default='Review', doc='Set the target ZenHub pipeline to '
                                                                                    'handle events for.')


def get_config():
    config = ConfigManager(environments=[
        ConfigOSEnv()
    ])
    return config.with_options(BotConfig())
