import json
import logging
import os
import time

import requests


class Base(object):
    def __init__(self, api_client_id, api_client_secret, auth_token):
        self.BASE_API_ENDPOINT = "https://api.medproid.com"

        self.api_client_id = api_client_id
        self.api_client_secret = api_client_secret

        if (auth_token is None) or (auth_token["authTokenExpires"] < int(time.time())):
            self.authorized = self._authorize_token()
        else:
            self.access_token = auth_token["authToken"]
            self.token_type = auth_token["authTokenType"]
            self.token_expire = auth_token["authTokenExpires"]
            self.authorized = True

        self.headers = None
        self.url = None
        self.status_code = 200

        self.logger = logging.getLogger(__name__)

    """ Send a standard OAuth 2.0 request using client
        credentials to get an access token
    """
    def _authorize_token(self) -> bool:
        data = {"grant_type": "client_credentials", "client_secret": self.api_client_secret, "client_id": self.api_client_id}

        header = {
            "User-Agent": "Python/3.9",
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate,br",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        r = requests.post(
            url=f"{self.BASE_API_ENDPOINT}/v1/authorize/token",
            data=data,
            headers=header,
        )
        if r.status_code == 200:
            self.access_token = r.json()["access_token"]
            self.token_type = r.json()["token_type"]
            self.token_expire = int(time.time()) + int(r.json()["expires_in"])
            return True
        else:
            self.access_token = None
            self.token_type = None
            self.token_expire = 0
            self.logger.error(f"Error: Could not obtain access token. ({r.status_code})")
            self.logger.error(f"Details: {json.dumps(r.json())}")
            return False

    def _get_header(self) -> dict:
        header = {
            "User-Agent": "Python/3.9",
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate,br",
            "Connection": "keep-alive",
        }

        if self.access_token is not None:
            if self.authorized is True:
                if self.token_expire > int(time.time()):
                    header["Authorization"] = f"{self.token_type} {self.access_token}"
                else:
                    # Access Token expired
                    self.authorized = self._authorize_token()
                    header["Authorization"] = f"{self.token_type} {self.access_token}"
            else:
                # Access Token not authorized
                self.authorized = self._authorize_token()
                header["Authorization"] = f"{self.token_type} {self.access_token}"

        return header

    def _do_get(self, endpoint, header, params) -> list:
        url = f"{self.BASE_API_ENDPOINT}{endpoint}"

        if params is None:
            r = requests.get(url=url, headers=header)
        else:
            r = requests.get(url=url, params=params, headers=header)

        # print(r.url)
        # print(params)
        self.url = r.url
        self.headers = r.headers
        self.status_code = r.status_code

        if r.status_code == 200:
            return r.json()
        else:
            return []

    def _do_post(self, endpoint, header, data) -> list:
        url = f"{self.BASE_API_ENDPOINT}{endpoint}"

        if data is None:
            r = requests.post(url=url, headers=header)
        else:
            r = requests.post(url=url, data=json.dumps(data), headers=header)

        self.url = r.url
        self.headers = r.headers
        self.status_code = r.status_code

        rv = []

        if r.status_code == 200:
            try:
                rv = r.json()
            except json.decoder.JSONDecodeError as jde:
                self.logger.exception(jde)

        return rv


    def getToken(self) -> dict:
        return {"authToken": self.access_token, "authTokenType": self.token_type, "authTokenExpires": self.token_expire}

    def ping(self) -> dict:
        r = requests.get(url=self.BASE_API_ENDPOINT, headers=self._get_header())

        self.headers = r.headers
        self.url = r.url
        self.status_code = r.status_code

        if r.status_code == 200:
            return r.json()
        else:
            return {}
