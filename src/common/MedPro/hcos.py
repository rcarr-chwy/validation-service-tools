from .base import Base


class HCOS(Base):
    def __init__(self, api_client_id=None, api_client_secret=None, auth_token=None):
        super().__init__(
            api_client_id=api_client_id,
            api_client_secret=api_client_secret,
            auth_token=auth_token,
        )

    """ Get one Health Care Organization detail record
    """
    def getDetailRecord(self, medpro_id: int) -> list:
        endpoint = f"/v1/hcos/{medpro_id}"
        header = self._get_header()
        params = None
        rv = self._do_get(endpoint, header, params)
        return rv

    """ Get a list of Health Care Organization detail records
    """
    def getDetailRecords(self, medpro_ids: list) -> list:
        endpoint = "/v1/hcos"
        data = {"ids": medpro_ids}
        header = self._get_header()
        header["Content-Type"] = "application/json-patch+json"
        rv = self._do_post(endpoint, header, data)
        return rv
