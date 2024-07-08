import urllib.error
import urllib.request
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed, RetryCallState
from tenacity.wait import wait_base


class retry_http_429(retry_if_exception):
    """Retry strategy that retries if the exception is an ``HTTPError`` with
    a 429 status code.

    """
    def is_http_429_error(exception):
            return (
                    isinstance(exception, urllib.error.HTTPError) and
                    exception.getcode() == 429
                    )
    def __init__(self) -> None:
        super().__init__(predicate=self.is_http_429_error)


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