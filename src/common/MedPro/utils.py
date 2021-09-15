import os
import json
import time

from .hcps import HCPS


def token_check(tokenFilename: str, clientId: str, clientSecret: str):
    authToken = None
    if os.path.exists(tokenFilename):
        with open(tokenFilename, "r") as token:
            authToken = json.load(token)

    if (authToken is None) or (authToken["authTokenExpires"] < int(time.time())):
        hcps = HCPS(api_client_id=clientId, 
                    api_client_secret=clientSecret)
        authToken = hcps.getToken()

        with open(tokenFilename, "w") as token:
            json.dump(authToken, token)

    return authToken


