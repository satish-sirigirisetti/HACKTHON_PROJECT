"""Consistent application logger configuration."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a named logger using the application-wide configured handlers."""
    return logging.getLogger(name)