
from singletons.config_manager import ConfigManager

class ConfigManager:
    _instance = None


    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance


    def _initialize(self):
        self.settings = {
            "DEFAULT_PAGE_SIZE": 20,
            "ENABLE_ANALYTICS": True,
            "RATE_LIMIT": 100
        }


    def get_setting(self, key):
        return self.settings.get(key)


    def set_setting(self, key, value):
        self.settings[key] = value


config1 = ConfigManager()
config2 = ConfigManager()


assert config1 is config2  # Both instances should be the same
config1.set_setting("DEFAULT_PAGE_SIZE", 50)
assert config2.get_setting("DEFAULT_PAGE_SIZE") == 50
