"""Store definitions used across multiple importers."""

import logging
import random
import time
import traceback
from enum import StrEnum
from typing import Any


class PlayerRole(StrEnum):
    """The available roles for a player."""

    GOALKEEPER = "G"
    DEFENDER = "D"
    MIDFIELDER = "M"
    ATTACKER = "A"


def log_fatal_error(
    logger: logging.Logger,
    item_id: Any,
    item_name: str,
) -> None:
    """Log a fatal error and raise the exception.

    Args:
    ----
        logger: the logger to use.
        item_id: the id of the item being extracted, added to the log message.
        item_name: the name of the item being extracted, added to the log message
            to provide context.
    
    """
    exception = traceback.format_exc()
    logger.exception(
        "Stopping the extraction at %s %s due to error: %s",
        item_id,
        item_name,
        exception,
        stack_info=True,
    )


def sleep_not_to_overload_the_website(sleep_time: int) -> None:
    """Sleep for a random time around the provided sleep time."""
    seconds_sleep = random.randint(sleep_time - 5, sleep_time + 5)
    time.sleep(seconds_sleep)
