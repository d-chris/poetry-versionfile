from __future__ import annotations

import sys
import typing as t

from pyinstaller_versionfile import __create
from pyinstaller_versionfile.metadata import MetaData
from pyinstaller_versionfile.metadata import MetadataKwargs


if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


if t.TYPE_CHECKING:
    from pathlib import Path


def read_toml(
    pyproject: t.Optional[Path] = None,
) -> MetadataKwargs:
    """
    Reading values from [tool.versionfile] section in a TOML file and returning as
    `MetadataKwargs`.

    If `tomlfile` is None or does not exist, returns an empty `MetadataKwargs`.

    - version: str
    - company_name: str
    - file_description: str
    - internal_name: str
    - legal_copyright: str
    - original_filename: str
    - product_name: str
    - translations: list[int]
    """

    if pyproject is None or not pyproject.is_file():
        return MetadataKwargs()

    toml = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    tool: dict = toml.get("tool", {})
    versionfile: dict = tool.get("versionfile", {})

    kwargs = {}

    # for key in MetadataKwargs.__annotations__:
    for name, key in MetaData.key_conversion.items():
        for k in {key, key.replace("_", "-"), name}:
            if k in versionfile:
                kwargs[key] = versionfile[k]
                break

    return MetadataKwargs(**kwargs)


def from_distribution(
    output_file: Path,
    distname: str,
    pyproject: str = None,
    **kwargs,
) -> int:
    """
    Create a version file from the distribution metadata.
    """

    result = 0 if output_file.is_file() else 1

    m = MetaData.from_distribution(distname)
    # meta = m.__dict__
    meta = {k: getattr(m, k) for k in MetaData.key_conversion.values()}

    param = read_toml(pyproject)

    meta.update(param)
    meta.update({k: v for k, v in kwargs.items() if v is not None})

    __create(MetaData(**meta), str(output_file))

    print(output_file.resolve(True))

    return result
