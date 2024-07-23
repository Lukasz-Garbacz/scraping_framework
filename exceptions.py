class NoDataError(Exception):
    """Server response is empty."""

class MaxRetriesExceeded(Exception):
    """Maximum retries value has been exceeded."""