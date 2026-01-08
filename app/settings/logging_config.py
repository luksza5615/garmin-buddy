import logging
import logging.config
import os
from typing import Any

_DEFAULT_LOGGING_LEVEL = "INFO"
_VALID_LOGGING_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_state = {"configured": False}

def setup_logging() -> None:
    if _state["configured"]:
        return

    level, default_level_used = _get_logging_level()

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": level,
                "stream": "ext://sys.stdout",
            }
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
    }

    logging.config.dictConfig(config)

    if default_level_used:
        logging.getLogger(__name__).warning(
            "Missing LOG_LEVEL in environment settings. Value set to default: %s", _DEFAULT_LOGGING_LEVEL
        ) 
        
    _state["configured"] = True

def _get_logging_level() -> tuple[str, bool]:
    logging_level = os.getenv("LOG_LEVEL")
    default_used = False
    if not logging_level:
        default_used = True
        
        return _DEFAULT_LOGGING_LEVEL, default_used
        
    if logging_level not in _VALID_LOGGING_LEVELS:
        raise ValueError(
            f"Incorrect LOG_LEVEL set in environment. Allowed: {_VALID_LOGGING_LEVELS}, but set: {logging_level}"
        )
    
    return logging_level, default_used
