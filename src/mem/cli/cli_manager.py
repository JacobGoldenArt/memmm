import click
from mem.config.config_manager import ConfigManager
from mem.cli.cli_manager import CLIManager
from mem.utils.logging_setup import setup_logging, set_logger_levels

# Initialize logging at the time of module loading to capture all events right from startup.
setup_logging()


@click.group()
@click.option(
    "-v",
    "--verbosity",
    type=click.Choice(["min", "med", "max", "bug"]),
    default="min",  # Set the default logging level to minimum to avoid verbose logging by default.
    help="Control the logging verbosity.",
)
@click.option(
    "-m",
    "--module",
    type=str,
    default=None,
    help="Specify a single module to log, or log all if not specified.",
)
@click.pass_context
def cli(ctx, verbosity, module):
    """
    This is the main CLI group function that sets up the context for managing the chat application.
    It initializes logging levels based on user inputs.
    """
    set_logger_levels(verbosity, module)
    ctx.ensure_object(dict)
    ctx.obj["LOG_VERBOSITY"] = verbosity
    ctx.obj["LOG_MODULE"] = module


@click.command(help="Starts the chat application with optional configuration.")
@click.option(
    "-p", "--preset", type=str, default="", help="Name of the preset to load."
)
@click.option(
    "-u", "--update", is_flag=True, help="Interactively update the config file."
)
@click.pass_context
def chat(ctx, preset, update):
    """
    This command starts the chat application. It can load a preset configuration or update configurations interactively.
    """
    config_manager = ConfigManager()  # Assume instantiation details
    cli_manager = CLIManager(config_manager)

    if preset:
        cli_manager.config_manager.load_preset(preset)
        print(f"Preset {preset} loaded.")
    if update:
        cli_manager.update_config_interactively()

    chat_config = cli_manager.config_manager.get_temp_config()
    cli_manager.chat_loop.run_loop(chat_config)


cli.add_command(chat)

if __name__ == "__main__":
    cli()
