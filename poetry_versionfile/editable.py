import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import click
import clickx

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

    match = re.search(r"(?<= Building editable for )(\S+)", stdout, re.MULTILINE)

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
            "resolve_path": True,
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


def pyproject(func=None):
    """
    Decorator to add a --toml click option with TomlFile type.
    """

    def decorator(f):
        return click.option(
            "--toml",
            type=TomlFile(),
            default=None,
            help="Path to pyproject.toml with version information.",
        )(f)

    return decorator(func) if callable(func) else decorator


@click.command(short_help="Create version file from local package.")
@click.argument(
    "input-path",
    type=click.Path(
        exists=True,
        file_okay=False,
        readable=True,
        path_type=Path,
    ),
)
@click.argument(
    "output-file",
    type=click.Path(
        writable=True,
        dir_okay=False,
        path_type=Path,
    ),
    default="version_file.txt",
)
@click.option(
    "--toml",
    is_flag=True,
    default=False,
    help="Use pyproject.toml for metadata.",
)
@click.option(
    "--uninstall/--no-uninstall",
    default=False,
    is_flag=True,
    help="Uninstall the package after creating the version file.",
    show_default=True,
)
@clickx.traceback()
def package(
    input_path: Path,
    output_file: Path,
    toml: bool,
    uninstall: bool = True,
) -> int:
    """
    Install a local package in editable mode, extract its package name,
    read optional version parameters from a TOML [tool.versionfile] section,
    and create a version file from the package distribution.
    """

    pyproject = input_path.joinpath("pyproject.toml").resolve(True) if toml else None

    with pip_editable(input_path, uninstall=uninstall) as package:

        return from_distribution(
            output_file,
            package,
            pyproject=pyproject,
        )


@click.command(short_help="Create version file from poetry package.")
@click.argument(
    "pyproject",
    type=TomlFile(),
)
@click.argument(
    "output_file",
    type=click.Path(
        writable=True,
        dir_okay=False,
        path_type=Path,
    ),
    default="version_file.txt",
)
@click.option(
    "--uninstall/--no-uninstall",
    default=False,
    is_flag=True,
    help="Uninstall the package after creating the version file.",
    show_default=True,
)
@clickx.traceback()
def poetry(
    pyproject: Path,
    output_file: Path,
    uninstall: bool,
) -> int:
    """
    Install a poetry package in editable mode, extract its package name,
    read optional version parameters from a TOML [tool.versionfile] section,
    and create a version_file.txt.
    """
    with pip_editable(pyproject.parent, uninstall=uninstall) as package:

        return from_distribution(
            output_file=output_file,
            distname=package,
            pyproject=pyproject,
        )


if __name__ == "__main__":
    package()
