# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module for parsing and rendering a navigation table."""

import re
import string
import typing

from . import types_
from .exceptions import NavigationTableParseError

_WHITESPACE = r"\s*"
_TABLE_HEADER_REGEX = (
    rf"{_WHITESPACE}\|"
    rf"{_WHITESPACE}level{_WHITESPACE}\|"
    rf"{_WHITESPACE}path{_WHITESPACE}\|"
    rf"{_WHITESPACE}navlink{_WHITESPACE}\|{_WHITESPACE}"
)
_TABLE_HEADER_PATTERN = re.compile(_TABLE_HEADER_REGEX, re.IGNORECASE)
_TABLE_PATTERN = re.compile(rf"[\s\S]*{_TABLE_HEADER_REGEX}[\s\S]*\|?", re.IGNORECASE)
_FILLER_ROW_REGEX_COLUMN = rf"{_WHITESPACE}-+{_WHITESPACE}\|"
_FILLER_ROW_PATTERN = re.compile(rf"{_WHITESPACE}\|{_FILLER_ROW_REGEX_COLUMN * 3}{_WHITESPACE}")
_LEVEL_REGEX = rf"{_WHITESPACE}(\d+){_WHITESPACE}"
_PATH_REGEX = rf"{_WHITESPACE}([\w-]+){_WHITESPACE}"
_NAVLINK_TITLE_REGEX = rf"[\w\- {string.punctuation}]+?"
_NAVLINK_LINK_REGEX = r"[\w\/-]*"
_NAVLINK_REGEX = (
    rf"{_WHITESPACE}\[{_WHITESPACE}({_NAVLINK_TITLE_REGEX}){_WHITESPACE}\]{_WHITESPACE}"
    rf"\({_WHITESPACE}({_NAVLINK_LINK_REGEX}){_WHITESPACE}\){_WHITESPACE}"
)
_ROW_PATTERN = re.compile(rf"{_WHITESPACE}\|{_LEVEL_REGEX}\|{_PATH_REGEX}\|{_NAVLINK_REGEX}\|")


def _filter_line(line: str) -> bool:
    """Check whether a line should be parsed.

    Args:
        line: The line to check.

    Returns:
        Whether the line should be parsed.
    """
    if _TABLE_HEADER_PATTERN.match(line) is not None:
        return True
    if _FILLER_ROW_PATTERN.match(line) is not None:
        return True
    if _ROW_PATTERN.match(line) is not None:
        return False
    return True


def _line_to_row(line: str) -> types_.TableRow:
    """Parse a markdown table line.

    Args:
        line: The line to process.

    Returns:
        The parsed row.

    Raises:
        NavigationTableParseError: if no match is found for the line.
    """
    match = _ROW_PATTERN.match(line)

    if match is None:
        raise NavigationTableParseError(f"Invalid table row, {line=!r}")

    level = int(match.group(1))
    path = match.group(2)
    navlink_title = match.group(3)
    navlink_link = match.group(4)

    return types_.TableRow(
        level=level,
        path=path,
        navlink=types_.Navlink(title=navlink_title, link=navlink_link or None),
    )


def from_page(page: str) -> typing.Iterator[types_.TableRow]:
    """Create an instance based on a markdown page.

    Algorithm:
        1.  Extract the table based on a regular expression looking for a 3 column table with
            the headers level, path and navlink (case insensitive). If the table is not found,
            assume that it is equivalent to a table without rows.
        2.  Process the rows line by line:
            2.1. If the row matches the header or filler pattern, skip it.
            2.2. Extract the level, path and navlink values.

    Args:
        page: The page to extract the rows from.

    Returns:
        The parsed rows from the table.
    """
    match = _TABLE_PATTERN.match(page)

    if match is None:
        return iter([])

    table = match.group(0)
    return (_line_to_row(line) for line in table.splitlines() if not _filter_line(line))
