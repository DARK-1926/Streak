import os
import subprocess
import sys
import logging
import shlex
import platform
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

# Configure logging for production-grade observability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("LocalCoder.Core")

@dataclass
class CommandResult:
    """Data class to hold the result of a subprocess execution."""
    stdout: str
    stderr: str
    returncode: int
    command: str
    timestamp: datetime = field(default_factory=datetime.now)

class CommandExecutionError(Exception):
    """Custom exception for failures during command execution."""
    pass

class ShellExecutor:
    """
    A robust executor for system commands designed to prevent common shell injection
    and parsing errors, specifically addressing 'eq was unexpected at this time'
    which occurs when unquoted variables or comparison operators are passed to 
    the Windows command processor (cmd.exe).
    """

    def __init__(self, use_shell: bool = False):
        """
        Initializes the executor.
        
        :param use_shell: If True, executes via the system shell. 
                          Note: Setting this to True on Windows can trigger 
                          parsing errors if arguments are not properly escaped.
        """
        self.use_shell = use_shell
        self.is_windows = platform.system() == "Windows"

    def _sanitize_argument(self, arg: str) -> str:
        """
        Ensures arguments are properly quoted to prevent shell interpretation
        of special characters like &, |, <, >, (, ), [, ], and comparison operators.
        """
        if not arg:
            return '""'
        
        # If the argument contains special characters, wrap it in double quotes
        # This prevents 'eq' or '==' from being interpreted by cmd.exe
        special_chars = ['&', '|', '<', '>', '(', ')', '[', ']', '^', '%', '!', '=']
        if any(char in arg for char in special_chars):
            # Escape existing double quotes by doubling them
            escaped_arg = arg.replace('"', '""')
            return f'"{escaped_arg}"'
        
        return arg

    def execute(self, cmd_list: List[str], env: Optional[Dict[str, str]] = None) -> CommandResult:
        """
        Executes a command safely.
        
        :param cmd_list: A list of command arguments.
        :param env: Environment variables to pass to the subprocess.
        :return: CommandResult object.
        :raises CommandExecutionError: If the command fails.
        """
        # If we are using the shell, we must join the command into a single string
        # and ensure every part is safely quoted to prevent 'eq was unexpected' errors.
        if self.use_shell:
            if self.is_windows:
                # On Windows, we must be extremely careful with how we join commands
                # to prevent the shell from misinterpreting comparison operators.
                sanitized_parts = [self._sanitize_argument(part) for part in cmd_list]
                full_command = " ".join(sanitized_parts)
            else:
                # On Unix-like systems, shlex handles shell-style quoting
                full_command = " ".join(shlex.quote(part) for part in cmd_list)
        else:
            # When use_shell=False, subprocess handles the list directly, 
            # which is the safest way to avoid shell parsing errors.
            full_command = cmd_list

        logger.debug(f"Executing command: {full_command}")

        try:
            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=self.use_shell,
                text=True,
                env=env or os.environ.copy()
            )
            
            stdout, stderr = process.communicate()
            returncode = process.returncode

            if returncode!= 0:
                logger.error(f"Command failed with exit code {returncode}: {stderr.strip()}")
                # We don't raise immediately to allow the caller to decide how to handle errors
            
            return CommandResult(
                stdout=stdout,
                stderr=stderr,
                returncode=returncode,
                command=str(cmd_list)
            )

        except Exception as e:
            logger.exception("An unexpected error occurred during command execution.")
            raise CommandExecutionError(f"Failed to execute command: {str(e)}")

class ErrorFixerEngine:
    """
    The core logic for LocalCoder, responsible for analyzing and fixing
    environment-related errors.
    """

    def __init__(self, executor: ShellExecutor):
        self.executor = executor

    def check_environment_integrity(self) -> bool:
        """
        Checks if the current environment contains variables that might cause
        shell parsing errors (e.g., unquoted paths with spaces or special chars).
        """
        logger.info("Performing environment integrity check...")
        integrity_passed = True
        
        for key, value in os.environ.items():
            if any(char in value for char in ['&', '(', ')', '<', '>', '|']):
                logger.warning(f"Potential shell collision detected in ENV variable: {key}={value}")
                # In a real production scenario, we might flag this for<pad><pad>
                # but for this task, we are just logging the risk.
                integrity_passed = False
        
        return integrity_passed

    def run_diagnostic(self, command: List[str]) -> None:
        """
        Runs a diagnostic command and reports results.
        """
        logger.info(f"Running diagnostic: {' '.join(command)}")
        try:
            result = self.executor.execute(command)
            if result.returncode == 0:
                logger.info("Diagnostic successful.")
                print(f"Output:\n{result.stdout}")
            else:
                logger.error(f"Diagnostic failed. Error: {result.stderr}")
        except CommandExecutionError as e:
            logger.error(f"Diagnostic execution failed: {e}")

class LocalCoderApp:
    """
    Main Application Entry Point.
    """

    def __init__(self):
        # We default to use_shell=False to avoid the 'eq was unexpected' error
        # which is caused by the shell interpreting the command string.
        self.executor = ShellExecutor(use_shell=False)
        self.engine = ErrorFixerEngine(self.executor)

    def run(self):
        logger.info("Starting LocalCoder Engine...")
        
        # 1. Check environment
        self.engine.check_environment_integrity()

        # 2. Example: Running a safe command
        # We use a list to avoid shell interpretation of special characters
        self.engine.run_diagnostic([sys.executable, "--version"])

        # 3. Example: Simulating a command that might fail on Windows if unquoted
        # If we were to run: subprocess.run("if %VAR%==val", shell=True)
        # It would fail with 'eq was unexpected at this time'.
        # By using use_shell=False and passing a list, we bypass the CMD parser.
        logger.info("Demonstrating safe execution of complex arguments...")
        safe_cmd = [sys.executable, "-c", "print('Testing equality logic safely')"]
        self.engine.run_diagnostic(safe_cmd)

        logger.info("LocalCoder execution completed.")

if __name__ == "__main__":
    app = LocalCoderApp()
    app.run()