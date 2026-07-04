import os
import json
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str):
        """
        Initialize the ConfigManager with a path to the configuration file.
        
        :param config_path: The path to the configuration file.
        """
        self.config_path = config_path
        self.config_data: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """
        Load the configuration from the specified file. If the file does not exist,
        it will be created with default settings.
        
        :raises RuntimeError: If there is an error loading the configuration.
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    self.config_data = json.load(file)
            else:
                self.config_data = self._default_config()
                self.save_config()
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")

    def save_config(self) -> None:
        """
        Save the current configuration to the specified file.
        
        :raises RuntimeError: If there is an error saving the configuration.
        """
        try:
            with open(self.config_path, 'w') as file:
                json.dump(self.config_data, file, indent=4)
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration: {e}")

    def _default_config(self) -> Dict[str, Any]:
        """
        Generate and return the default configuration.
        
        :return: A dictionary containing the default configuration.
        """
        return {
            "formatter": "autopep8",
            "linter": "pylint",
            "test_runner": "pytest"
        }

    def get_config(self, key: str) -> Any:
        """
        Get the value of a specific configuration key.
        
        :param key: The key for the configuration value.
        :return: The value associated with the key, or None if the key does not exist.
        """
        return self.config_data.get(key)

    def set_config(self, key: str, value: Any) -> None:
        """
        Set the value of a specific configuration key and save the updated configuration.
        
        :param key: The key for the configuration value.
        :param value: The new value to set for the key.
        """
        self.config_data[key] = value
        self.save_config()