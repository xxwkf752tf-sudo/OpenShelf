#!/usr/bin/env python3
from setuptools import setup, find_packages
setup(
    name="openshelf", version="1.0.0",
    description="OpenShelf - Local AI Coding Assistant for Windows",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=["PyQt6>=6.7.0","aiohttp>=3.9.0","PyYAML>=6.0","cryptography>=43.0.0","keyring>=25.0.0"],
)
