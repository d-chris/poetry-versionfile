from __future__ import annotations

import typing as t

from pre_commit_hooks.end_of_file_fixer import fix_file
from pre_commit_hooks.trailing_whitespace_fixer import _fix_file as fix_whitespace


if t.TYPE_CHECKING:
    import os


def fix_eof(filename: str | os.PathLike) -> bool:
    """Ensure the file ends with a single newline."""

    with open(filename, "rb+") as file_obj:
        return bool(fix_file(file_obj))


def format_file(filename: str | os.PathLike) -> bool:
    """Remove tailing whitespace and ensure a single newline at the end of the file."""

    space = fix_whitespace(str(filename), False, None)
    eof = fix_eof(filename)

    return space and eof
