"""
Configuration module for Local Duplicate Code Detector & Refactor Assistant (LDCDRA).
Provides centralized configuration for external tool commands, timeouts, and other settings.
"""

import os
from typing import List, Dict, Any

class Config:
    """
    Configuration class encapsulating all settings for LDCDRA.
    """
    # Default command definitions as lists of arguments for subprocess.
    # These assume the tools are available in the system PATH or as local scripts.
    # If a tool is not found, the tool will raise a RuntimeError when invoked.
    DEFAULT_REFACTOR_COMMAND: List[str] = ["./refactor", "--apply"]
    DEFAULT_DUPLICATE_DETECTOR_COMMAND: List[str] = ["./duplicate_code_detector", "--check"]
    DEFAULT_LINT_COMMAND: List[str] = ["pylint"]
    DEFAULT_FORMAT_COMMAND: List[str] = ["black", "--check"]
    DEFAULT_ANALYSIS_COMMAND: List[str] = ["radon", "cc"]

    def __init__(self) -> None:
        # Load configuration from environment variables with fallback to defaults.
        self.refactor_command: List[str] = self._get_command(
            "LDCDRA_REFACTOR_CMD", self.DEFAULT_REFACTOR_COMMAND
        )
        self.duplicate_detector_command: List[str] = self._get_command(
            "LDCDRA_DUPLICATE_DETECTOR_CMD", self.DEFAULT_DUPLICATE_DETECTOR_COMMAND
        )
        self.lint_command: List[str] = self._get_command(
            "LDCDRA_LINT_CMD", self.DEFAULT_LINT_COMMAND
        )
        self.format_command: List[str] = self._get_command(
            "LDCDRA_FORMAT_CMD", self.DEFAULT_FORMAT_COMMAND
        )
        self.analysis_command: List[str] = self._get_command(
            "LDCDRA_ANALYSIS_CMD", self.DEFAULT_ANALYSIS_COMMAND
        )

        # Numeric settings
        self.timeout_seconds: int = int(os.getenv("LDCDRA_TIMEOUT_SECONDS", "30"))
        self.max_file_size_kb: int = int(os.getenv("LDCDRA_MAX_FILE_SIZE_KB", "1024"))
        self.verbose: bool = os.getenv("LDCDRA_VERBOSE", "false").lower() == "true"

    @staticmethod
    def _get_command(env_var: str, default: List[str]) -> List[str]:
        """
        Retrieve a command list from environment variable `env_var`.
        If the variable is set, split it into a list respecting simple quoting.
        Otherwise, return the default list.
        """
        raw = os.getenv(env_var)
        if not raw:
            return default.copy()
        # Simple splitting on whitespace; for advanced quoting, consider shlex.split.
        return raw.split()

    def get_command(self, tool: str) -> List[str]:
        """
        Return the command list for the specified tool.
        Supported tools: 'refactor', 'duplicate_detector', 'lint', 'format', 'analysis'.
        """
        mapping: Dict[str, List[str]] = {
            "refactor": self.refactor_command,
            "duplicate_detector": self.duplicate_detector_command,
            "lint": self.lint_command,
            "format": self.format_command,
            "analysis": self.analysis_command,
        }
        if tool not in mapping:
            raise ValueError(f"Unknown tool '{tool}'")
        return mapping[tool].copy()

    def validate(self) -> None:
        """
        Validate that all required commands are non-empty and contain at least one argument.
        Raises RuntimeError if any command is invalid.
        """
        for attr_name in (
            "refactor_command",
            "duplicate_detector_command",
            "lint_command",
            "format_command",
            "analysis_command",
        ):
            cmd = getattr(self, attr_name)
            if not cmd:
                raise RuntimeError(f"Configuration error: {attr_name} is empty")
            if not all(isinstance(arg, str) for arg in cmd):
                raise RuntimeError(f"Configuration error: {attr_name} contains non-string elements")

# Global configuration instance for easy import.
config = Config()

# Optional: If the script is run directly, print the configuration.
if __name__ == "__main__":
    import json
    print(json.dumps({k: getattr(config, k) for k in dir(config) if not k.startswith("_")}, indent=2))