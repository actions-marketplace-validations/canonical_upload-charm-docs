# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Helper functions for tests."""

import typing
from pathlib import Path

from src import index


def create_metadata_yaml(content: str, path: Path) -> None:
    """Create the metadata file.

    Args:
        content: The text to be written to the file.
        path: The directory to create the file in.

    """
    metadata_yaml = path / index.METADATA_FILENAME
    metadata_yaml.write_text(content, encoding="utf-8")


def assert_substrings_in_string(substrings: typing.Iterable[str], string: str) -> None:
    """Assert that a string contains substrings.

    Args:
        string: The string to check.
        substrings: The sub strings that must be contained in the string.

    """
    for substring in substrings:
        assert substring in string  # nosec
