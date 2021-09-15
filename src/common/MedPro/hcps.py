import urllib.parse

from .base import Base


class HCPS(Base):
    def __init__(self, api_client_id=None, api_client_secret=None, auth_token=None):
        super().__init__(
            api_client_id=api_client_id,
            api_client_secret=api_client_secret,
            auth_token=auth_token,
        )

    """ Get a list of Health Care Practioners that meet
        the criteria. The response is typically limited
        to 50-100 records and can return up to 500 records
    """
    def search(
        self,
        stateOfLicense: str = None,
        lastName: str = None,
        firstName: str = None,
        middleName: str = None,
        slnStateLicenseNumber: str = None,
        npiNumber: str = None,
        deaNumber: str = None,
        cdsNumber: str = None,
        slnProfessionalDesignation: str = None,
        addressLine1: str = None,
        city=None,
        addressState: str = None,
        zip: str = None,
        country: str = None,
        query: str = None,
        pageNumber: int = 0,
        pageSize: int = 0,
    ) -> list:

        params = {
            "stateOfLicense": stateOfLicense,
            "lastName": lastName,
            "firstName": firstName,
            "middleName": middleName,
            "slnStateLicenseNumber": slnStateLicenseNumber,
            "npiNumber": npiNumber,
            "deaNumber": deaNumber,
            "cdsNumber": cdsNumber,
            "slnProfessionalDesignation": slnProfessionalDesignation,
            "addressLine1": addressLine1,
            "city": city,
            "addressState": addressState,
            "zip": zip,
            "country": country,
            "query": query,
            "pageNumber": pageNumber,
            "pageSize": pageSize,
        }
        forDeletion = []
        for i in params.keys():
            if params[i] in [None, 0]:
                forDeletion.append(i)
        for j in forDeletion:
            del params[j]

        endpoint = "/v1/hcps/search"
        header = self._get_header()
        params = urllib.parse.urlencode(params, safe=":+")
        rv = self._do_get(endpoint, header, params)
        return rv

    """ Get one Health Care Practitioner detail record
    """
    def getDetailRecord(self, medpro_id: str) -> dict:
        endpoint = f"/v1/hcps/{medpro_id}"
        header = self._get_header()
        params = None
        rv = self._do_get(endpoint, header, params)
        return rv

    """ Get a list of Health Care Practioner detail records
    """
    def getDetailRecords(self, medpro_ids: list) -> list:
        endpoint = "/v1/hcps"
        data = {"ids": medpro_ids}
        header = self._get_header()
        header["Content-Type"] = "application/json-patch+json"
        rv = self._do_post(endpoint, header, data)
        return rv

    """ Get one Health Care Practioner detail record that
        matches based on configurable rules
    """
    def match(
        self,
        stateOfLicense: str = None,
        lastName: str = None,
        firstName: str = None,
        middleName: str = None,
        slnStateLicenseNumber: str = None,
        npiNumber: str = None,
        deaNumber: str = None,
        cdsNumber: str = None,
        meNumber: str = None,
        slnProfessionalDesignation: str = None,
        addressLine1: str = None,
        city=None,
        addressState: str = None,
        zip: str = None,
        source: str = None,
    ) -> list:

        params = {
            "stateOfLicense": stateOfLicense,
            "lastName": lastName,
            "firstName": firstName,
            "middleName": middleName,
            "slnStateLicenseNumber": slnStateLicenseNumber,
            "npiNumber": npiNumber,
            "deaNumber": deaNumber,
            "cdsNumber": cdsNumber,
            "meNumber": meNumber,
            "slnProfessionalDesignation": slnProfessionalDesignation,
            "addressLine1": addressLine1,
            "city": city,
            "addressState": addressState,
            "zip": zip,
            "source": source,
        }
        forDeletion = []
        for i in params.keys():
            if params[i] in [None, 0]:
                forDeletion.append(i)

        for k in forDeletion:
            del params[k]

        endpoint = "/v1/hcps/match"
        header = self._get_header()
        header["content-type"] = "application/json-patch+json"
        rv = self._do_get(endpoint, header, params)
        return rv
