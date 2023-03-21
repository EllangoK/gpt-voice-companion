import json

class ConfigManager:

    CONFIG_FILENAME = "config.json"
    
    def __init__(self, args_dict: dict, defaults: dict):
        self.env = args_dict
        self.defaults = defaults
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.CONFIG_FILENAME, 'r', encoding="utf8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_config(self, config):
        with open(self.CONFIG_FILENAME, 'w', encoding="utf8") as f:
            json.dump(config, f, indent=4)

    def __getitem__(self, key) -> str|bool|float|int:
        return self.env.get(key) or self.config.get(key) or self.defaults[key]

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save_config(self.config)
