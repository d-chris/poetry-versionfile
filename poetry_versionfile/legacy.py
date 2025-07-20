from functools import wraps

import pyinstaller_versionfile.__main__ as pv


@wraps(pv.create_version_file)
def create_versionfile(*args, **kwargs):
    return pv.create_version_file(*args, **kwargs)


@wraps(pv.make_version)
def make_version(*args, **kwargs):
    return pv.make_version(*args, **kwargs)
