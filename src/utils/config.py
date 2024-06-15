import yaml

class ConfigDict(dict):
    def __getattr__(self, name):
        try:
            value = self[name]
            if isinstance(value, dict):
                return ConfigDict(value)
            return value
        except KeyError:
            raise AttributeError(f"No such attribute: {name}")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"No such attribute: {name}")


class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self):
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)
        return ConfigDict(config)

    def __getattr__(self, item):
        return getattr(self._config, item)
    
def get_config(config_path = "../config.yaml") -> Config:
    return Config(config_path)