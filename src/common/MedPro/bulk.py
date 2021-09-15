from .base import Base


class Bulk(Base):
    def __init__(self, api_client_id=None, api_client_secret=None, auth_token=None):
        super().__init__(
            api_client_id=api_client_id,
            api_client_secret=api_client_secret,
            auth_token=auth_token,
        )

    def statuses(self, filetype: str = None, pageNumber: int = 0, pageSize: int = 0) -> list:
        params = {"filetype": filetype, "pageNumber": pageNumber, "pageSize": pageSize}
        toDelete = []
        for i in params.keys():
            if params[i] in [None, 0]:
                toDelete.append(i)
        for t in toDelete:
            del params[t]

        endpoint = "/v1/bulk/statuses"
        header = self._get_header()
        rv = self._do_get(endpoint, header, params)
        return rv

    def status(self, fileToken: str) -> list:
        params = {}

        endpoint = f"/v1/bulk/statuses/{fileToken}"
        header = self._get_header()
        rv = self._do_get(endpoint, header, params)
        return rv

    def getProcessedFile(self, file_token: str, batch_number: int) -> list:
        endpoint = f"/v1/bulk/{file_token}"
        header = self._get_header()
        params = {"batchNumber": batch_number}
        rv = self._do_get(endpoint, header, params)
        return rv

    def finalizeProcessedFile(self, file_token: str) -> list:
        endpoint = f"/v1/bulk/{file_token}/finalize"
        data = None
        header = self._get_header()
        rv = self._do_post(endpoint, header, data)
        return rv
