import logging

import litellm
from rich.logging import RichHandler


def setup_logging():
    logging.basicConfig(
        level=logging.NOTSET,  # Capture all logs initially
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


def set_logger_levels(verbosity: str = None, module_name: str = None):
    """Adjusts the logging level and LiteLLM's verbosity based on the provided verbosity argument."""
    # Default to suppress all logging
    level = logging.CRITICAL + 1
    litellm_verbose = False  # Default LiteLLM verbose mode

    if verbosity == "min":
        level = logging.INFO
    elif verbosity == "med":
        level = logging.WARNING
        litellm_verbose = True
    elif verbosity == "max":
        level = logging.ERROR
        litellm_verbose = True
    elif verbosity == "bug":
        level = logging.DEBUG
        litellm_verbose = True

    # Explicitly set the root logger level, in addition to configuring basicConfig
    logging.getLogger().setLevel(level)  # This ensures the level is applied correctly
    logging.basicConfig(level=level)
    litellm.set_verbose = litellm_verbose

    # Log the status of LiteLLM verbose mode and logging initialization
    if level <= logging.INFO:  # Only log if the level is INFO or more verbose
        logging.info(
            f"Logging initialized with level: {logging.getLevelName(level)}, LiteLLM verbose mode: {'enabled' if litellm_verbose else 'disabled'}"
        )
    # If module_name is specified, adjust logging level for that module only
    if module_name:
        logging.getLogger(module_name).setLevel(level)
    else:
        # Set the logging level for all loggers
        for logger_name in logging.root.manager.loggerDict:
            logging.getLogger(logger_name).setLevel(level)


# Initial setup call
setup_logging()

# if __name__ == "__main__":
#     logger = logging
#     set_logger_levels("min")
#     logger.info("Logging initialized with min level")
# set_logger_levels("min")
# logger.info("Logging initialized")
# set_logger_levels("med")
# logger.warning("Logging warning initialized")
# set_logger_levels("max")
# logger.error("Logging max initialized")
