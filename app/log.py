"""Logging configuration module for the PDB Mirror application.

This module sets up the basic logging configuration for the application,
including log level, format, and provides a logger instance.
"""

import logging

__all__ = ["log"]

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Main application logger instance
log = logging.getLogger(__name__)
