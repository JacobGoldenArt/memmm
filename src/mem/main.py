import logging
from mem.cli.cli_manager import cli
from mem.config.config_manager import ConfigManager
from mem.utils.logging_setup import setup_logging


def setup_initial_configurations():
    """Load or initialize configuration settings that are critical for the app."""
    config_manager = ConfigManager()
    try:
        config_manager.load_global_config()  # Assuming a method to load global configs
    except Exception as e:
        logging.error(f"Failed to load configurations: {e}")
        raise SystemExit("Could not load initial configurations. Exiting.")


def main():
    """Main function to kickstart the CLI with proper initialization and error handling."""
    setup_logging()  # Ensure logging is configured before anything else
    setup_initial_configurations()  # Setup configurations before starting the CLI

    try:
        cli()  # Start the CLI interface
    except Exception as e:
        logging.critical(f"Unhandled exception in the CLI: {e}", exc_info=True)
        raise SystemExit(f"Exiting due to an unhandled exception: {e}")


if __name__ == "__main__":
    main()
