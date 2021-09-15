import os
import click
import json

import common.config as config
from common.datastore import DataStore
from common.MedPro.hcps import HCPS
from common.MedPro.utils import token_check

    
db = DataStore('support.sqlite')

def grab_code(stateOrProvince: str) -> str:
    if stateOrProvince is None:
        return ''

    if len(stateOrProvince) == 2:
        return stateOrProvince

    if len(stateOrProvince) > 3:
        sql = "SELECT Code FROM states WHERE state_or_province = ?;"
        params = (stateOrProvince, )
        rv = db.do_query(sql, params)

        if len(rv) == 0:
            return ''
        else:
            return rv[0]['Code']


@click.command()
@click.option('-i',  '--input',required=True, type=str)
def process_datadog(input):  
    hcps = HCPS(
        api_client_id=config.MEDPRO_API_CLIENT_ID,
        api_client_secret=config.MEDPRO_API_CLIENT_SECRET,
        auth_token=token_check(config.CLIENT_TOKEN_FILENAME,
                               config.MEDPRO_API_CLIENT_ID, 
                               config.MEDPRO_API_CLIENT_SECRET
                               )
    )

    file1 = open(input, 'r')
    logs = file1.readlines()
    print(len(logs))

    with open('processed_logs.txt', 'w') as of:
        headerLine = "Kyrios ID\tName\tState\tLicense\t# Results\tMedPro Id\tMedPro State\tMedPro License\tIn Universe\n"
        of.write(headerLine)

        for line in logs:
            payload = json.loads(line)['result']

            if 'vet' in payload.keys():

                if payload['env'] == 'prd':
                    vet = json.loads(payload['vet'])
                    vet_id = vet.get('id')
                    vet_dr = vet.get('doctorName')
                    if 'address' in vet['provider'].keys():
                        vet_st = grab_code(vet['provider']['address'].get('state', ''))
                    else:
                        vet_st = '' 

                    # Licenses are inconsistent so using them for searching on MedPro
                    # is bad and will only cause pain.
                    tmpLicenses = vet.get('licenses', [])
                    if len(tmpLicenses) == 0:
                        vet_lic = vet.get('vet_id','')
                    else:
                        vet_lic = tmpLicenses[0].get('licenseNumber', '')

                    vet_tmp = vet_dr.split(' ')
                    if len(vet_tmp) == 2:
                        vet_firstName = vet_tmp[0].strip()
                        vet_lastName = vet_tmp[1].strip()
                        vet_middleName = None
                    elif len(vet_tmp) == 3:
                        vet_firstName = vet_tmp[0].strip()
                        vet_middleName = vet_tmp[1].replace('.','')
                        vet_lastName = vet_tmp[2].strip()

                    rv = hcps.search(stateOfLicense=vet_st, 
                                    lastName=vet_lastName, 
                                    firstName=vet_firstName, 
                                    middleName=vet_middleName
                                    )

                    if len(rv) == 1:
                        vet_medpro_id = rv[0].get('medProID','')
                        vet_medpro_state = rv[0].get('stateLicenseInfo_LicenseState', '')
                        vet_in_universe = rv[0].get('customerData_InUniverse', '')
                        vet_medpro_license = rv[0].get('stateLicense_StateLicenseNumber', '')
                    else:
                        vet_medpro_id = ''
                        vet_medpro_state = ''
                        vet_in_universe = ''
                        vet_medpro_license = ''

                    dataLine = f"{vet_id}\t{vet_dr}\t{vet_st}\t{vet_lic}\t{len(rv)}\t{vet_medpro_id}\t{vet_medpro_state}\t{vet_medpro_license}\t{vet_in_universe}\n"
                    of.write(dataLine)

                else:
                    print(f"Unknown env ({payload['env']})")


if __name__ == '__main__':  
    process_datadog()
