from typing import Optional

from .base import Base


class Universe(Base):
    def __init__(self, api_client_id=None, api_client_secret=None, auth_token=None):
        super().__init__(
            api_client_id=api_client_id,
            api_client_secret=api_client_secret,
            auth_token=auth_token,
        )

    """ Returns True if the provider is in the universe,
        False otherwise.
    """
    def inUniverse(self, medpro_id: int) -> bool:
        endpoint = f"/v1/universe/{medpro_id}"
        header = self._get_header()
        params = None
        rv = self._do_get(endpoint, header, params)
        if "inUniverse" in rv.keys():
            return rv["inUniverse"]
        else:
            return False

    """ Add the provider to the unverse.
    """
    def addToUniverse(self, medpro_id: str, client_id: Optional[str] = None) -> dict:
        endpoint = f"/v1/universe/{medpro_id}?clientid={client_id}"
        data = None
        header = self._get_header()
        rv = self._do_post(endpoint, header, data)
        return rv
