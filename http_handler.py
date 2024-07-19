from io import TextIOWrapper
import urllib.error
import urllib.request
import json

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed, RetryCallState
from tenacity.wait import wait_base

from settings import Settings as st


class JSONParser:
    json_file: TextIOWrapper
    handling_policy: dict

    def __init__(self, error_code) -> None:
        self.read()
        self.get_params(error_code)

    def read(self) -> None:
        with open(st.http_handling_path) as json_file:
            self.json_file = json.load(json_file)
    
    @classmethod
    def get_params(self, error_code: int) -> None:
        try:
            default_dict = self.json_file['default_policy']
            error_dict = self.json_file['error_codes'][str(error_code)]
        except KeyError:
            error_dict = self.json_file['default_policy']
        
        #wait_strategy
        try:
            if error_dict['wait_strategy'] == 'wait_after_header':
                self.handling_policy['wait_strategy'] = get_wait_strat
            else:
                raise KeyError
        except KeyError:
            self.handling_policy['wait_strategy'] = wait_fixed

        #fallback_wait
        try:
            if error_dict['fallback_wait'] == 'wait_fixed':
                self.handling_policy['fallback_wait'] = wait_fixed
            else:
                raise KeyError
        except KeyError:
            self.handling_policy['fallback_wait'] = wait_fixed

        #wait_time
        try:
            self.handling_policy['wait_time'] = error_dict['wait_time']
        except KeyError:
            self.handling_policy['wait_time'] = default_dict['wait_time']
        
        #max_retries
        try:
            self.handling_policy['max_retries'] = error_dict['max_retries']
        except KeyError:
            self.handling_policy['max_retries'] = default_dict['max_retries']


class get_wait_strat(wait_base):
    """Wait strategy that tries to wait for the length specified by
    the Retry-After header, or the underlying wait strategy if not.

    Otherwise, wait according to the fallback strategy.
    """

    def __init__(self) -> None:
        pass

    def __call__(self, retry_state: RetryCallState) -> int:
        exc = retry_state.outcome.exception()
        params_dict = JSONParser.get_params(error_code= exc.getcode())
        #TODO TUTAJ CHYBA DODAC PARAMSY
        #wait strategy
        if params_dict['wait_strategy'] == 'wait_after_header':
            retry_after = exc.headers.get("Retry-After")
        elif isinstance(params_dict['wait_strategy'], wait_fixed):
            retry_after = params_dict['wait_strategy'](params_dict['wait_time'])
        try:
            return int(retry_after)
        except (TypeError, ValueError):
            #fallback strategy
            return params_dict['fallback_wait'](params_dict['wait_time'])


class retry_if_http_error(retry_if_exception):
    """Retry strategy that retries if the exception is an ``HTTPError``
    """
    def is_http_error(exception):
            return isinstance(exception, urllib.error.HTTPError)
    def __init__(self) -> None:
        super().__init__(predicate=self.is_http_error)