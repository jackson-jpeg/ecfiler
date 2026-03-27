"""Tests for logging configuration."""

import logging

import pytest

from ecfiler.logging import get_logger


class TestLogging:
    def test_get_logger(self) -> None:
        logger = get_logger("ecfiler.test")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "ecfiler.test"

    def test_logger_has_handlers(self) -> None:
        logger = get_logger("ecfiler.test2")
        # The root ecfiler logger should have handlers
        root = logging.getLogger("ecfiler")
        assert len(root.handlers) >= 1

    def test_different_modules_get_different_loggers(self) -> None:
        a = get_logger("ecfiler.module_a")
        b = get_logger("ecfiler.module_b")
        assert a is not b
        assert a.name != b.name

    def test_logger_level(self) -> None:
        root = logging.getLogger("ecfiler")
        assert root.level <= logging.INFO
