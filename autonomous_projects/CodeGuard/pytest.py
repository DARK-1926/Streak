class raises:
    """
    Context manager for asserting that a specific exception is raised.
    Usage:
        with pytest.raises(ExpectedException):
            # code that should raise ExpectedException
    """
    def __init__(self, exc):
        self.exc = exc

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Return True if an exception was raised and it matches the expected type
        if exc_type is None:
            # No exception was raised
            return False
        return issubclass(exc_type, self.exc)


class _Mark:
    """
    Simple stub for pytest.mark with a parametrize decorator.
    The decorator is a no-op and returns the original function unchanged.
    """
    def parametrize(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator


mark = _Mark()


def fixture(func):
    """
    No-op fixture decorator.
    Simply returns the function unchanged.
    """
    return func