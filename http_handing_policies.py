from dataclasses import dataclass
from http_handler import wait_after_header
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed, RetryCallState
from tenacity.wait import wait_base


@dataclass
class HTTPErrorPolicies:
    error_list = {
        404: {'fallback_wait': wait_fixed
             ,'wait_time': 1
             ,'max_retries': 5
            },
        429: {'wait_strategy': wait_after_header
             ,'fallback_wait': wait_fixed
             ,'wait_time': 30
             ,'max_retries': 3
            },
        500: {'fallback_wait': wait_fixed
             ,'wait_time': 5
             ,'max_retries': 5
            }
    }

    default_policy = {
        'fallback_wait': wait_fixed
        ,'wait_time': 10
        ,'max_retries': 3
    }