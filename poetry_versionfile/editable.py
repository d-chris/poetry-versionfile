import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import click

from .versionfile import from_distribution

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def pip_install_editable(package_path: str) -> str:

    directory = Path(package_path).resolve(True)

    if not directory.is_dir():
        raise ValueError(f"Provided path '{package_path}' is not a directory.")

    stdout = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-color",
            "--disable-pip-version-check",
            "--editable",
            str(directory),
        ],
        stderr=subprocess.STDOUT,
        text=True,
    )

    match = re.search(
        r"(?<=^Building wheels for collected packages: )(.*)$", stdout, re.MULTILINE
    )

    try:
        return match.group(0).strip()
    except Exception as e:
        raise RuntimeError(f"Failed to parse output: {e}") from e


def pip_uninstall(package_name: str) -> int:

    return subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "--no-color",
            "--disable-pip-version-check",
            "uninstall",
            "-y",
            package_name,
        ],
    )


@contextmanager
def pip_editable(package_path: str, uninstall: bool = True):
    """Context manager to install a package as editable."""
    try:
        package = pip_install_editable(package_path)

        yield package
    except Exception as e:
        raise RuntimeError(
            f"Failed to install package as editable from {package_path}"
        ) from e
    else:
        if uninstall:
            pip_uninstall(package)


class TomlFile(click.Path):
    """
    Custom click.Path for handling TOML files.
    """

    def __init__(self):

        kwargs = {
            "file_okay": True,
            "exists": True,
            "dir_okay": False,
            "readable": True,
            "path_type": Path,
        }

        super().__init__(**kwargs)

        self.name = "PYPROJECT"

    def convert(self, value, param, ctx):
        value = super().convert(value, param, ctx)  # type: Path

        try:
            with value.open("rb") as f:
                tomllib.load(f)
        except Exception as e:
            self.fail(f"{e} in {value}", param, ctx)

        return value


@click.command(short_help="Create version file from local package.")
@click.argument(
    "input-path",
    type=click.Path(
        exists=True,
        file_okay=False,
        readable=True,
    ),
)
@click.argument(
    "output-file",
    type=click.Path(
        writable=True,
        dir_okay=False,
    ),
    default="version_file.txt",
)
@click.option(
    "--toml",
    type=TomlFile(),
    default=None,
    help="Path to pyproject.toml with version information.",
)
def package(input_path: str, output_file: str, toml: Path):
    """
    Install a local package in editable mode, extract its package name,
    read optional version parameters from a TOML [tool.versionfile] section,
    and create a version file from the package distribution.
    """

    with pip_editable(input_path) as package:

        from_distribution(
            output_file,
            package,
            pyproject=toml,
        )


if __name__ == "__main__":
    package()
