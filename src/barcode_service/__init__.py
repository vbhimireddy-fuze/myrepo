# coding=utf-8

from .barcodemain import main

__all__ = ["main", "version"]
__version__ = "99.99.99999+fffffff"

def version() -> str:
    return __version__
