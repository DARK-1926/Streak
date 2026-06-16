from pathlib import Path

from setuptools import setup, find_packages

# Read the long description from README if available
this_dir = Path(__file__).parent
readme_path = this_dir / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""

# Load requirements
requirements_path = this_dir / "requirements.txt"
install_requires = (
    requirements_path.read_text(encoding="utf-8").splitlines()
    if requirements_path.is_file()
    else []
)

setup(
    name="localcodingassistant",
    version="0.1.0",
    description="A minimal, modular CLI tool for local LLM‑based code assistance.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name <you@example.com>",
    packages=find_packages(where=".", include=["lca", "lca.*"]),
    python_requires=">=3.8",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "lca=lca.cli:lca",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)