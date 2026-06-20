#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script for the CodeGuard package.

This script configures the distribution package for CodeGuard, ensuring that
the installation dependencies are consistent with the project's
`requirements.txt`.  The `install_requires` list has been updated to use
`simhash==2.1.2` to match the version specified in the requirements file.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the long description from README.md
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Package metadata
PACKAGE_NAME = "codeguard"
PACKAGE_VERSION = "0.1.0"
PACKAGE_DESCRIPTION = "A lightweight tool for detecting duplicate code snippets in Python projects."
PACKAGE_URL = "https://github.com/example/codeguard"
AUTHOR = "Your Name"
AUTHOR_EMAIL = "you@example.com"
LICENSE = "MIT"

# Runtime dependencies
INSTALL_REQUIRES = [
    # Updated to match requirements.txt
    "simhash==2.1.2",
    # Additional dependencies required by CodeGuard
    "pygments>=2.15.0",
    "termcolor>=2.3.0",
    "colorama>=0.4.6",
]

# Optional dependencies for development and testing
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.4.0",
        "mypy>=1.8.0",
        "black>=23.12.0",
    ],
    "test": [
        "pytest>=7.4.0",
    ],
}

# Entry points for console scripts
ENTRY_POINTS = {
    "console_scripts": [
        "codeguard=codeguard:main",
    ],
}

# Classifiers for PyPI
CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Testing",
    "Topic :: Software Development :: Quality Assurance",
]

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description=PACKAGE_DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=PACKAGE_URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points=ENTRY_POINTS,
    classifiers=CLASSIFIERS,
    project_urls={
        "Bug Tracker": f"{PACKAGE_URL}/issues",
        "Documentation": f"{PACKAGE_URL}/docs",
        "Source Code": PACKAGE_URL,
    },
)