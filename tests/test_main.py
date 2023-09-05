#!/usr/bin/env python3

from click.testing import CliRunner
from vl53_400_lib.main import cli
from unittest.mock import MagicMock, patch
import unittest


class TestMain(unittest.TestCase):
    def test_cli(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage: cli [OPTIONS]" in result.output
        assert "Options:" in result.output
        self.assertRegex(result.output, "--help(\\s+)Show this message and exit.")
