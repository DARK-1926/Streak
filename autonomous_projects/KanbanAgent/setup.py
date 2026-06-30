from setuptools import setup, find_packages

setup(
    name="KanbanAgent",
    version="0.1.0",
    description="A compact, cross-platform Kanban board application for task management.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="KanbanAgent Team",
    author_email="support@kanbanagent.dev",
    url="https://github.com/kanbanagent/kanbanagent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Task Management",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "black>=23.0.0,<24.0.0",
            "mypy>=1.0.0,<2.0.0",
            "flake8>=6.0.0,<7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kanban-agent=kanban_board:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)