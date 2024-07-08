import urllib.error
import urllib.request
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed, RetryCallState
from tenacity.wait import wait_base

def http_retry(func):
    def inner1(*args, **kwargs):
        
        print("before Execution")
        
        # getting the returned value
        returned_value = func(*args, **kwargs)
        print("after Execution")
        
        # returning the value to the original frame
        return returned_value
        
    return inner1


class wait_after_header(wait_base):
    """Wait strategy that tries to wait for the length specified by
    the Retry-After header, or the underlying wait strategy if not.

    Otherwise, wait according to the fallback strategy.
    """
    fallback: wait_fixed

    def __init__(self, fallback: wait_fixed) -> None:
        self.fallback = fallback

    def __call__(self, retry_state: RetryCallState):
        exc = retry_state.outcome.exception()
        if isinstance(exc, urllib.error.HTTPError):
            retry_after = exc.headers.get("Retry-After")
            try:
                return int(retry_after)
            except (TypeError, ValueError):
                pass

        return self.fallback(retry_state)