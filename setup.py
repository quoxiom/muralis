"""Compatibility shim for Muralis.

Pyproject.toml is the canonical build configuration (metadata, dependencies,
extras and entry points). This file exists only so legacy tooling that still
invokes ``setup.py`` works; ``pip``/``build`` prefer ``pyproject.toml`` and
ignore the redundant kwargs here.

The package version comes from ``muralis.__version__`` via
``[tool.setuptools.dynamic] version = {attr = ...}`` in ``pyproject.toml``.
"""

from setuptools import setup

setup()
