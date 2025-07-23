from __future__ import annotations

import typing as t

from pre_commit_hooks.end_of_file_fixer import fix_file
from pre_commit_hooks.trailing_whitespace_fixer import _fix_file as fix_whitespace


if t.TYPE_CHECKING:
    import os


def fix_eof(filename: str | os.PathLike, **kwargs) -> bool:
    """Ensure the file ends with a single newline."""

    with open(filename, "rb+", **kwargs) as file_obj:
        return fix_file(file_obj) > 0


def format_file(filename: str | os.PathLike, **kwargs) -> bool:
    """
    Remove tailing whitespace and ensure a single newline at the end of the file.

    Returns `True` if the file was modified, `False` otherwise.
    """

    space = fix_whitespace(
        str(filename),
        kwargs.get("is_markdown", False),
        kwargs.get("chars", None),
    )
    eof = fix_eof(filename)

    return space and eof
