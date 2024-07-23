from io import TextIOWrapper
from time import sleep
import urllib.error
import urllib.request
import json

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed, RetryCallState
from tenacity.wait import wait_base

from settings import Settings as st
from http_handler import JSONParser
from exceptions import MaxRetriesExceeded

def http_retry(func):
    def inner1():
        wait_time = None
        retries = 0
        max_retries = 1
        while retries < max_retries:
            try:
                func()
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
            

    return inner1