from typing import Optional

from .base import Base


class Inquiries(Base):
    def __init__(self, api_client_id=None, api_client_secret=None, auth_token=None):
        super().__init__(
            api_client_id=api_client_id,
            api_client_secret=api_client_secret,
            auth_token=auth_token,
        )

    """ Create a DRP Requestas a Jira ticket
    """
    def createDRPRequest(
        self, 
        userName: str = None,
        customerName: str = None,
        firstName: str = None,
        lastName: str = None,	
        title: str = None,
        email: str = None,
        phone: str = None,	
        medProId: int = 0,
        clientId: str = None,
        hcpFirstName: str = None,
        hcpLastName: str = None,
        stateLicenseNumber: str = None,
        npiNumber: str = None,
        deaNumber: str = None,
        cdsNumber: str = None,
        licenseState: str = None,
        professionalDesignation: str = None,
        description: str = None,
        summary: str = None
    ) -> str:
        endpoint = "/v1/inquiries"
        data = {
        "userName": userName,
        "customerName": customerName,
        "firstName": firstName,
        "lastName": lastName,	
        "title": title,
        "email": email,
        "phone": phone,	
        "medProId": medProId,
        "clientId": clientId,
        "hcpFirstName": hcpFirstName,
        "hcpLastName": hcpLastName,
        "stateLicenseNumber": stateLicenseNumber,
        "npiNumber": npiNumber,
        "deaNumber": deaNumber,
        "cdsNumber": cdsNumber,
        "licenseState": licenseState,
        "professionalDesignation": professionalDesignation,
        "description": description,
        "summary": summary 
        }
        header = self._get_header()
        rv = self._do_post(endpoint, header, data)
        return rv
