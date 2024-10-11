from time import sleep
import urllib.error
import urllib.request

from http_handler import JSONParser
from exceptions import MaxRetriesExceeded

def http_retry(func):
    def inner1(*args, **kwargs):
        wait_time = None
        retries = 0
        max_retries = 1
        while retries < max_retries:
            try:
                return_value = func(*args, **kwargs)
                break
            except urllib.error.HTTPError as exc:
                params_dict = JSONParser(exc).handling_policy
                max_retries = params_dict['max_retries']
                try:
                    #cases when wait_time needs to be updated each try
                    if wait_time is None or params_dict['wait_strategy'] == 'wait_after_header':
                        wait_time = params_dict['wait_time']
                    elif params_dict['wait_strategy'] == 'const_increase':
                        wait_time += params_dict['wait_time']
                except KeyError:
                    wait_time = params_dict['fallback_wait']
                sleep(wait_time)
                retries += 1
            raise MaxRetriesExceeded(f'Retries exceeded: {max_retries}')
        return return_value
            

    return inner1