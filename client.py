import requests
import pandas as pd
import urllib3

from time import sleep
from requests.adapters import HTTPAdapter, Retry, Response
from tenacity import retry, stop_after_attempt, wait_fixed
from urllib.request import getproxies

from http_429_handler import retry_http_429, wait_after_http_429
from settings import Settings as st
from exceptions import NoDataError


class RawClient:
    session: requests.Session

    def __init__(self) -> None:
        self.session = requests.Session()
        if st.disable_safety:
            pd.set_option('future.no_silent_downcasting', True)
            urllib3.disable_warnings()
            self.session.trust_env= False
        retries = Retry(
                        total=5,
                        backoff_factor=0.1,
                        status_forcelist=[407, 500, 502, 503, 504]
                        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.headers.update({'user-agent': 'scraper'})


    @retry(
            retry=retry_http_429(),
            wait=wait_after_http_429(fallback=wait_fixed(60)),
            stop=stop_after_attempt(5)
            )
    def fetch_one(self, website_address: str, params_dict: dict = {}) -> Response:
        """Download website and return response content, wait if HTTP 429 error.

        Keyword arguments:
            website_address -- full address of website to download, including 'http://', 
            params_dict [optional] -- parameters to add to the GET request for RestAPI compatibility
        Return value:
            .content parameter of requests.adapters.Response class
        Exceptions raised:
            NoDataError -- raised when server response content is empty, 
            requests.HTTPError -- raised when a HTTP error is returned by server
        """
        response = self.session.get(
                            website_address
                            ,params= params_dict
                            ,verify= False if st.disable_safety else True
                            ,proxies= getproxies()
                            )
        response.raise_for_status()
        if len(response.content) == 0:
                    raise NoDataError
        return response.content


    def fetch_all(self, params_dict: dict, website_address, wait_download: int = 0, stop_on_exc: bool = False) -> list:
        """Download list of websites using the fetch_one method.

         Keyword arguments:
            params_dict [optional] -- parameters to add to the GET request for RestAPI compatibility
            website_address -- list of full addresses of websites to download, including 'http://'
            wait_download -- number of seconds to wait between downloads (default 0)
            stop_on_exc -- bool if method should stop on first exception thrown (default False)
        Return value:
            list of .content parameters of requests.adapters.Response class
        Exceptions raised (only when stop_on_exc is set to True):
            NoDataError -- raised when server response content is empty
            requests.HTTPError -- raised when a HTTP error is returned by server
        """
        responce_list = []
        if not isinstance(website_address, list):
            website_address = [website_address]

        for website in website_address:
            try:
                responce_list.append(self.fetch_one(params_dict, website))
            except (NoDataError, requests.HTTPError) as exc:
                pass
            if stop_on_exc:
                return responce_list
            sleep(wait_download)
        return responce_list