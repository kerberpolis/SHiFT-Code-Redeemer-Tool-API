"""
Definitions of config variables for different environments.
"""
import logging
import os


class AppConfig:
    env_name = ""
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET = None, None, None, None
    ENCRYPTION_KEY = None
    API_ROOT = "/borderlands-code-crawler/"
    VERSION = "v1"
    BASE_PATH = API_ROOT + VERSION
    DOCS_URL = BASE_PATH + "/docs"
    REDOC_URL = BASE_PATH + "/redoc"
    OPENAPI_URL = BASE_PATH + "/openapi.json"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    GITHUB_ACCESS_TOKEN = None

    def __init__(self):
        env_vars = [
            'TWITTER_CONSUMER_KEY',
            'TWITTER_CONSUMER_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_TOKEN_SECRET',
            'BORDERLANDS_ENCRYPTION_KEY',
            '_GITHUB_ACCESS_TOKEN'
        ]
        for env_var in env_vars:
            if env_var not in os.environ:
                raise Exception(f"Must have environment variable {env_var} set.")

        self.get_env_vars()

    def get_env_vars(self):
        # Twitter API credentials
        self.CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
        self.CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
        self.ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
        self.ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        # Encryption Key
        self.ENCRYPTION_KEY = os.getenv('BORDERLANDS_ENCRYPTION_KEY')

        # Github Token
        self.GITHUB_ACCESS_TOKEN = os.getenv('_GITHUB_ACCESS_TOKEN')


class DevelopAppConfig(AppConfig):
    env_name = "DEVELOP"
    logging_level = logging.DEBUG

    def __init__(self):
        super().__init__()


class ProductionAppConfig(AppConfig):
    env_name = "PRODUCTION"
    logging_level = logging.INFO

    def __init__(self):
        super().__init__()


environment_configs = dict(
    DEVELOP=DevelopAppConfig,
    PRODUCTION=ProductionAppConfig
    )


def get_config():
    """Return configuration settings based on ASSET_MONITOR_ENV.  Defaults to
    DEVELOP if not set or not recognised."""
    env = os.getenv("BORDERLANDS_CODE_ENV", "DEVELOP").upper()
    config = environment_configs.get(env, DevelopAppConfig)
    return config()
