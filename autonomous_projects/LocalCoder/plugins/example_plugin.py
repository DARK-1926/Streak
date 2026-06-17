"""
Example plugin for LocalCoder.

This plugin demonstrates how to extend the LocalCoder application by adding a simple
`greet` command. The command accepts a single positional argument `name` and prints
a friendly greeting to the console.

The plugin follows the expected interface for LocalCoder plugins:
* It exposes a top-level function `register_command(app)` that receives the
  application instance and registers the command using the application's
  command decorator.
* It uses type hints and comprehensive docstrings to aid static analysis,
  IDE autocompletion, and maintainability.

The design is intentionally minimal to keep the example lightweight while
still illustrating best practices such as dependency injection, clear
documentation, and graceful error handling.

"""

from __future__ import annotations

from typing import Any

# The application instance is expected to provide a `command` decorator.
# We import typing only; no runtime dependency on the application package.
# This keeps the plugin self‑contained and importable even if the main
# application is not present, which is useful for unit testing.

def _greet_command(name: str) -> None:
    """
    Print a friendly greeting to the console.

    Parameters
    ----------
    name : str
        The name of the person to greet. Leading and trailing whitespace is
        stripped to avoid accidental formatting issues.

    Notes
    -----
    The function is intentionally simple: it performs minimal validation
    (ensuring the name is not empty after stripping) and writes the greeting
    to standard output. If the name is empty, a generic greeting is used.
    """
    cleaned_name = name.strip()
    greeting = f"Hello, {cleaned_name}!" if cleaned_name else "Hello!"
    print(greeting)

def register_command(app: Any) -> None:
    """
    Register the ``greet`` command with the LocalCoder application.

    Parameters
    ----------
    app : Any
        The application instance. It must expose a ``command`` decorator
        that accepts a command name and returns a decorator used to wrap the
        command implementation.

    Raises
    ------
    AttributeError
        If the ``app`` object does not provide the required ``command`` attribute.
    """
    if not hasattr(app, "command"):
        raise AttributeError(
            "The provided app instance does not have a 'command' attribute. "
            "Ensure you are passing a valid LocalCoder application object."
        )

    @app.command("greet")
    def greet(name: str) -> None:
        """
        Command handler for the ``greet`` command.

        Parameters
        ----------
        name : str
            The name of the person to greet. This value is passed directly
            from the command line by the application framework.
        """
        _greet_command(name)

# End of file