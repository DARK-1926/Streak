from setuptools import setup, find_packages

setup(
    name="hn_summary",
    version="0.1.0",
    description="Extract titles and categories from raw Hacker News snippets",
    packages=find_packages(),
    python_requires=">=3.8",
    author="Agent BEAST",
    license="MIT",
)
