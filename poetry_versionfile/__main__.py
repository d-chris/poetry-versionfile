import functools
import os
import traceback as tb
from pathlib import Path

import click
from pyinstaller_versionfile import create_versionfile
from pyinstaller_versionfile import create_versionfile_from_distribution
from pyinstaller_versionfile import create_versionfile_from_input_file

from .editable import package
from .format import format_file


def options(func=None):
    """
    Decorator that adds common CLI options to a function.

    Parameters added:
    - output_file: str
    - version: Optional[str] = None
    - company_name: Optional[str] = None
    - file_description: Optional[str] = None
    - internal_name: Optional[str] = None
    - legal_copyright: Optional[str] = None
    - original_filename: Optional[str] = None
    - product_name: Optional[str] = None
    - translations: Optional[list[int]] = None
    """

    def decorator(func):
        @click.argument(
            "output-file",
            type=click.Path(writable=True, dir_okay=False),
            default="version_file.txt",
        )
        @click.option(
            "--version",
            type=str,
            help="Version of the file.",
        )
        @click.option(
            "--company-name",
            type=str,
            help="Company name for the file.",
        )
        @click.option(
            "--file-description",
            type=str,
            help="Description of the file.",
        )
        @click.option(
            "--internal-name",
            type=str,
            help="Internal name of the file.",
        )
        @click.option(
            "--legal-copyright",
            type=str,
            help="Legal copyright information.",
        )
        @click.option(
            "--original-filename",
            type=str,
            help="Original filename of the file.",
        )
        @click.option(
            "--product-name",
            type=str,
            help="Product name for the file.",
        )
        @click.option(
            "-t",
            "--translations",
            type=int,
            multiple=True,
            default=[1033, 1200],
            show_default=True,
            help="Translation IDs for the file.",
        )
        @click.option(
            "-q",
            "--quiet",
            is_flag=True,
            default=False,
            help="Suppress output messages.",
        )
        @click.option(
            "--fmt/--no-fmt",
            is_flag=True,
            default=True,
            help=format_file.__doc__,
            show_default=True,
        )
        @click.option(
            "--traceback",
            is_flag=True,
            default=False,
            help="Show traceback on error.",
        )
        @functools.wraps(func)
        def wrapper(quiet, traceback, fmt, **kwargs):

            with open(os.devnull, "w") as pipe:

                if quiet is False:
                    pipe = None

                try:
                    exitcode = func(**kwargs) or 0

                    file = Path(kwargs["output_file"]).resolve(True)

                    if fmt is True:
                        format_file(file)

                    click.echo(str(file), file=pipe)
                except (Exception, KeyboardInterrupt) as e:
                    exitcode = 3

                    if traceback:
                        msg = tb.format_exc()
                    else:
                        msg = str(e)

                    click.echo(msg, err=True, file=pipe)
                finally:
                    raise SystemExit(exitcode)

        return wrapper

    return decorator(func) if callable(func) else decorator


@click.group()
@click.version_option()
def cli():
    """
    Powered by `pyinstaller_versionfile`.

    Commandline interface to create a windows version-file from metadata stored in a
    simple self-written YAML file or obtained from an installed distribution.
    """

    pass


@cli.command(
    short_help="Create version file from arguments.",
    help=create_versionfile.__doc__,
)
@options()
def create(**kwargs):

    create_versionfile(**kwargs)


@cli.command(
    short_help="Create version file from YAML file.",
    help=create_versionfile_from_input_file.__doc__,
)
@click.argument(
    "input_file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
)
@options()
def yaml(**kwargs):

    create_versionfile_from_input_file(**kwargs)


@cli.command(
    short_help="Create version file from distribution.",
    help=create_versionfile_from_distribution.__doc__,
)
@click.argument(
    "distname",
    type=str,
)
@options()
def dist(**kwargs):

    create_versionfile_from_distribution(**kwargs)


cli.add_command(package)

if __name__ == "__main__":
    cli()
