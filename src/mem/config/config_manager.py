import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import tomli_w
import tomllib
from rich.console import Console

logger = logging.getLogger(__name__)

console = Console()


@dataclass
class ConfigManager:
    """The ConfigManager will handle getting and setting the cli config via the CLI.
    For safety, The user can't update the settings.toml file through the CLI.
    Instead, the user can update a temp file that is a copy of the presets.default table in settings.toml.
    The user can update the temp file with new settings and then if desired can save the temp file as
    a new preset in settings.toml.
    """

    # get the path of the project root directory: "__em"
    root_dir: str = field(init=False)
    app_dir: str = field(init=False)
    presets_dir: str = field(init=False)
    config_file: str = field(init=False)
    temp_config: str = field(init=False)
    config_choices: tuple = field(
        default=(
            "api_service",
            "model",
            "temperature",
            "max_tokens",
            "speech_to_text",
            "text_to_speech",
            "speech_model",
            "voice",
        )
    )

    def __post_init__(self):
        self.root_dir = os.path.dirname(
            os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
        )
        self.src_dir = os.path.join(self.root_dir, "mem")
        self.presets_dir = os.path.join(self.src_dir, "config", "_presets")
        self.config_file = os.path.join(self.src_dir, "config", "_app_config.toml")
        self.config = self._load_config()
        self.temp_config_file = os.path.join(
            self.src_dir, "config", "_temp_config.toml"
        )
        self.temp_config = self._load_temp_config()
        self._copy_default_to_temp_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load and return the configuration file."""
        try:
            with open(self.config_file, "rb") as f:
                return tomllib.load(f)
        except FileNotFoundError:
            logger.error(f"Error: Config file '{self.config_file}' not found.")
            return {}

    def _load_temp_config(self) -> Dict[str, Any]:
        """Load and return the temporary configuration file."""
        with open(self.temp_config_file, "rb") as f:
            return tomllib.load(f)

    def _copy_default_to_temp_config(self):
        """Copy the default settings to the temporary configuration file."""
        try:
            default_settings = self.config.get("cli", {}).get("default", {})
            with open(self.temp_config_file, "wb") as f:
                tomli_w.dump(default_settings, f)
                logger.info("Default settings copied to temporary configuration.")
        except Exception as e:
            logger.error(f"Failed to initialize temporary settings: {e}")
            raise e

    def get_temp_config(self) -> Optional[Dict]:
        """Public method to get the temp config, ensuring it's always fresh."""
        self.temp_config = self._load_temp_config()  # Reload from file
        logger.info(f"Here is the current temp config {self.temp_config}")
        return self.temp_config

    def update_temp_config(self, new_settings: Dict):
        """Update the temporary configuration with new settings."""
        try:
            # Update in-memory config first
            self.temp_config.update(new_settings)
            # Write updated config to file
            with open(self.temp_config_file, "wb") as f:
                tomli_w.dump(self.temp_config, f)
            console.log("Temporary settings updated.")
            # Ensure in-memory config is reloaded to reflect the file's current state
            self.temp_config = self._load_temp_config()
        except Exception as e:
            logger.error(f"Error updating temporary settings: {e}")

    def get_value_from_config(self, key_path: str) -> Optional[Any]:
        """Get a single setting value using a dot-notation key path."""
        current = self.config
        try:
            for key in key_path.split("."):
                if isinstance(current, list):
                    # If current is a list, return a list of values for the given key
                    return [item.get(key, None) for item in current]
                current = current[key]
            return current
        except KeyError:
            return None

    def get_list_values_from_config(self, list_name: str, key: str) -> List[Any]:
        """Get all values of a specific key from a list of dictionaries."""
        try:
            items = self.config.get(list_name, [])
            return [item.get(key, None) for item in items if key in item]
        except (TypeError, ValueError):
            return []

    def get_app_settings_from_config(
        self, settings_to_get: tuple
    ) -> Optional[Dict[str, Any]]:
        """Get the requested settings from the app_config.toml file."""
        settings = {}
        for key in settings_to_get:
            settings[key] = self.get_value_from_config(key)
        return settings if settings else None

    def get_aliases_for_models(self, llm_name: str) -> Optional[Dict[str, Any]]:
        """Get the aliases for the given model from the LLMS table."""
        try:
            llms = self.get_list_values_from_config("llms", llm_name)
            return llms[0].get("aliases", {})
        except Exception as e:
            logger.error(f"Failed to get aliases for model '{llms}': {e}")
        return None

    def save_as_preset(self, preset_name: str):
        """Save the temp config as a new preset."""
        temp_config = self.temp_config
        try:
            preset_file_path = os.path.join(
                self.presets_dir, f"{preset_name}_preset.toml"
            )
            with open(preset_file_path, "wb") as f:
                tomli_w.dump(temp_config, f)
                console.log(f"Preset '{preset_name}' saved.")
        except Exception as e:
            logger.error(f"Failed to save preset '{preset_name}': {e}")

    def list_presets(self):
        """List all the available presets."""
        try:
            presets = os.listdir(self.presets_dir)
            # remove _preset.toml from preset names
            presets = [preset.replace("_preset.toml", "") for preset in presets]
            return presets
        except Exception as e:
            logger.error(f"Failed to list presets: {e}")
        return []

    def load_preset(self, preset_name: str):
        """load a preset by name and save it as the temp config."""
        try:
            preset_file_path = os.path.join(
                self.presets_dir, f"{preset_name}_preset.toml"
            )
            with open(preset_file_path, "rb") as f:
                preset = tomllib.load(f)
            with open(self.temp_config_file, "wb") as f:
                tomli_w.dump(preset, f)
                logger.info(f"Configuration replaced with preset '{preset_name}'.")
        except Exception as e:
            logger.error(
                f"Failed to replace configuration with preset '{preset_name}': {e}"
            )

    def remove_preset(self, preset_name: str):
        """Remove a preset by name."""
        try:
            preset_file_path = os.path.join(
                self.presets_dir, f"{preset_name}_preset.toml"
            )
            os.remove(preset_file_path)
            logger.info(f"Preset '{preset_name}' removed.")
        except Exception as e:
            logger.error(f"Failed to remove preset '{preset_name}': {e}")


# if __name__ == "__main__":
# config_manager = ConfigManager()
# gets a single value from a table but cant retrieve a single value from a table inside a list.
# app_config = config_manager.get_value_from_config("cli.default.api_service")
# aliases = config_manager.get_aliases_from_llms("ollama")
# rprint(aliases)
# app_config = config_manager.get_list_values_from_config("llms", "together")
# if app_config and isinstance(app_config, list):
#     ollama_model_alias = app_config[0].get("aliases", {})
#     print(f"aliases: {ollama_model_alias}")
# else:
#     print("No aliases found.")
# get aliases object from llms table
# ollama_model_alias = app_config[0].get("aliases", {})
# app_config = config_manager.get_app_settings_from_config(("cli.exit_words", "cli.default.api_service"))
# rprint(ollama_model_alias)

# # Test loading the temporary configuration
# console.print("Initial Temp Config:")
# temp_config = config_manager.get_temp_config()
# console.print(temp_config)

# Test updating the temporary configuration
# console.print("\nUpdating Temp Config...")
# config_manager.update_temp_config({"api_service": "ollama", "model": "llama7b"})
# updated_temp_config = config_manager.get_temp_config()
# console.print(updated_temp_config)

# # Test saving the temporary configuration as a new preset
# console.print("\nSaving Temp Config as New Preset 'test'...")
# config_manager.save_as_preset("test")

# # List all presets after adding a new one
# console.print("\nListing Presets After Adding 'bathroom' Preset:")
# presets = config_manager.list_presets()
# console.print(presets)

# Test loading a preset (ensure "pirate" or any other test preset exists)
# console.print("\nLoading Preset 'pirate'...")
# config_manager.load_preset("pirate")
# console.print("Temp Config After Loading 'pirate' Preset:")
# pirate_config = config_manager.get_temp_config()
# console.print(pirate_config)

# Optionally, uncomment to test removing a preset
# console.print("\nRemoving Preset 'bathroom'...")
# config_manager.remove_preset("bathroom")
# console.print("Listing Presets After Removing 'bathroom' Preset:")
# presets_after_removal = config_manager.list_presets()
# console.print(presets_after_removal)
