from setuptools import setup, find_packages
import os

# Read the contents of README.md for the long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Define the required dependencies
install_requires = [
    "python-docx==0.8.11",
]

# Define the setup configuration
setup(
    name="DocxEditorLite",
    version="0.1.0",
    description="A lightweight, cross-platform DOCX editor.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/DocxEditorLite",
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.7",
)