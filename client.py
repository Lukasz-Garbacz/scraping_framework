import requests
import pandas as pd
import urllib3

from time import sleep
from requests.adapters import HTTPAdapter, Retry, Response
from retry_decorator import http_retry
from urllib.request import getproxies

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
        if st.default_retries:
            retries = Retry(
                            total=5,
                            backoff_factor=0.1,
                            status_forcelist=[407, 500, 502, 503, 504],
                            respect_retry_after_header= True
                            )
        else:
            retries = None
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.headers.update({'user-agent': 'scraper'})


    @http_retry
    def get_one(self, url: str, params_dict: dict = {}) -> Response.content:
        """Download website and return response content, wait if HTTP 429 error.

        Keyword arguments:
            url -- full address of website to download, including 'http://'
            params_dict [optional, Default: {}] -- parameters to add to the GET request for RestAPI compatibility
        Return value:
            requests.adapters.Response.content
        Exceptions raised:
            NoDataError -- raised when server response content is empty, 
            requests.HTTPError -- raised when a HTTP error is returned by server
        """
        response = self.session.get(
                            url
                            ,params= params_dict
                            ,verify= False if st.disable_safety else True
                            ,proxies= getproxies()
                            )
        response.raise_for_status()
        if len(response.content) == 0:
                    raise NoDataError
        return response.content


    def get_all(self, urls, params_dict: dict = {}, wait_download: int = 0, stop_on_exc: bool = False) -> list[Response.content]:
        """Download list of websites using the fetch_one method.

         Keyword arguments:
            urls -- list of full addresses of websites to download, including 'http://'
            params_dict [optional, Default: {}] -- parameters to add to the GET request for RestAPI compatibility
            wait_download [optional, Default: 0] -- number of seconds to wait between downloads (default 0)
            stop_on_exc [optional, Default: False] -- bool if method should stop on first exception thrown (default False)
        Return value:
            list of requests.adapters.Response.content parameters
        Exceptions raised (only when stop_on_exc is set to True):
            NoDataError -- raised when server response content is empty
            requests.HTTPError -- raised when a HTTP error is returned by server
        """
        responce_list = []
        if not isinstance(urls, list):
            try:
                urls = [urls]
            except TypeError:
                raise Exception(f'Wrong format of urls variable, accepted formats: str, list. Given format: {type(urls)}')

        for website in urls:
            try:
                responce_list.append(self.get_one(params_dict, website))
            except (NoDataError, requests.HTTPError) as exc:
                pass
            if stop_on_exc:
                return responce_list
            sleep(wait_download)
        return responce_list

    @http_retry
    def post_one(self, url: str, cert = None, data_dict: dict = None, json_dict: dict = None, auth: tuple = None) -> Response.content:
        """Download website and return response content, wait if HTTP 429 error.
        Keyword arguments:
            url -- full address of website to download, including 'http://'
            cert [optional, Default: None] -- string or tuple specifying a cert file or key
            data_dict [optional, Default: None] -- dictionary object to send to the specified url
            json_dict [optional, Default: None] -- JSON object to send to the specified url
        Return value:
            requests.adapters.Response.content
        Exceptions raised:
            NoDataError -- raised when server response content is empty, 
            requests.HTTPError -- raised when a HTTP error is returned by server
        """
        response = self.session.post(
                            url
                            ,data= data_dict
                            ,verify= False if st.disable_safety else True
                            ,proxies= getproxies()
                            ,cert= cert
                            ,json= json_dict
                            )
        response.raise_for_status()
        if len(response.content) == 0:
                    raise NoDataError
        return response.content