from io import TextIOWrapper
import urllib.error
import urllib.request
import json

from settings import Settings as st


class JSONParser:
    json_file: TextIOWrapper
    handling_policy: dict
    exception: urllib.error.HTTPError

    def __init__(self, exception: Exception) -> None:
        self.exception = exception
        self.read()
        self.get_params()

    def read(self) -> None:
        with open(st.http_handling_path) as json_file:
            self.json_file = json.load(json_file)
    
    def get_wait_strategy(self) -> int:
        try:
            retry_after = self.exception.headers.get("Retry-After")
            return int(retry_after)
        except (KeyError, TypeError, ValueError):
            return self.handling_policy['fallback_wait']

    def get_params(self) -> None:
        try:
            default_dict = self.json_file['default_policy']
            error_dict = self.json_file['error_codes'][str(self.exception.getcode())]
        except KeyError:
            error_dict = self.json_file['default_policy']
        
        #wait_time
        try:
            self.handling_policy['wait_time'] = error_dict['wait_time']
        except KeyError:
            self.handling_policy['wait_time'] = default_dict['wait_time']

        #wait_time
        try:
            self.handling_policy['fallback_wait'] = error_dict['fallback_wait']
        except KeyError:
            self.handling_policy['fallback_wait'] = default_dict['fallback_wait']

        #wait_strategy
        try:
            if error_dict['wait_strategy'] == 'wait_after_header':
                self.handling_policy['wait_time'] = self.get_wait_strategy()
            self.handling_policy['wait_strategy'] = error_dict['wait_strategy']
        except KeyError:
            self.handling_policy['wait_strategy'] = default_dict['wait_strategy']

        #max_retries
        try:
            self.handling_policy['max_retries'] = error_dict['max_retries']
        except KeyError:
            self.handling_policy['max_retries'] = default_dict['max_retries']


# class retry_if_http_error(retry_if_exception):
#     """Retry strategy that retries if the exception is an ``HTTPError``
#     """
#     def is_http_error(exception):
#             return isinstance(exception, urllib.error.HTTPError)
#     def __init__(self) -> None:
#         super().__init__(predicate=self.is_http_error)