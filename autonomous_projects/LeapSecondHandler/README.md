# LeapSecondHandler

## Overview
LeapSecondHandler is a Python application designed to handle and adjust for negative leap seconds in time-sensitive systems. The project ensures that these systems remain accurate and reliable, even when affected by the rare occurrence of a negative leap second. The application is built with a focus on algorithmic efficiency, security, and isolation, and includes a comprehensive unit test suite to validate its functionality.

## Architecture
The project is structured as follows:
- **leap_second_handler.py**: Contains the `LeapSecondHandler` class, which provides methods to check for and adjust timestamps during a negative leap second.
- **time_utils.py**: Provides utility functions for getting the current UTC time and converting timestamps from a specified timezone to UTC.
- **test_main.py**: Contains unit tests for the `LeapSecondHandler` and `time_utils` modules to ensure their correctness.
- **.gitignore**: Specifies files and directories to be ignored by Git.

## How it Works
### LeapSecondHandler Class
The `LeapSecondHandler` class is responsible for detecting and adjusting for negative leap seconds. It maintains a record of the last detected leap second and uses this information to determine if the system is currently affected by a leap second. If a leap second is detected, the class adjusts incoming timestamps by subtracting one second.

### Time Utilities
The `time_utils` module provides two key functions:
- `get_current_utc_time()`: Returns the current UTC time.
- `convert_to_utc(timestamp, timezone)`: Converts a given timestamp from a specified timezone to UTC.

### Testing
The `test_main.py` file contains unit tests for both the `LeapSecondHandler` and `time_utils` modules. These tests cover various scenarios, including simulating a leap second and verifying the correct adjustment of timestamps, as well as testing the accuracy of the time conversion functions.

## Setup Instructions
### Prerequisites
- Python 3.8 or higher
- `pytz` library (install using `pip install pytz`)

### Running the Tests
To run the unit tests, use the following command:
```sh
python -m unittest test_main.py
```

### Example Usage
To see an example of how to use the `LeapSecondHandler`, you can run the `leap_second_handler.py` script directly:
```sh
python leap_second_handler.py
```

This will output the current time and the adjusted time if a negative leap second is detected.

## Contribution
Contributions are welcome! Please follow the style guide and ensure that all changes are covered by unit tests.