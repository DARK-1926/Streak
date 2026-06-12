import sys
import pytest

if __name__ == '__main__':
    # Execute pytest on the tests package; ``-q`` for quiet output.
    exit_code = pytest.main(['-q', 'tests'])
    sys.exit(exit_code)
