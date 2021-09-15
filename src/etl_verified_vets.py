import click
import datetime
import numpy as np
import time
import pandas as pd

import common.config as config
from common.utils import print_progress_bar, check_version
from common.MedPro.hcps import HCPS
from common.MedPro.universe import Universe
from common.MedPro.utils import token_check
   

def clean_and_parse_name(fullName:str):
    try:
        if fullName in ['', ' ', None]:
            return {'firstName': '**NO NAME**', 
                    'middleName': '', 
                    'lastName': ''
                    }
        else:
            tmpName = fullName.replace('Dr. ', '')
            tmpName = tmpName.replace('Dr ', '')

            tmpName = tmpName.replace('Jr.', '')
            tmpName = tmpName.replace('Jr', '')
            tmpName = tmpName.replace(', Jr.', '')

            tmpName = tmpName.replace(' Dvm', '')
            tmpName = tmpName.replace(' DVM', '')
            tmpName = tmpName.replace(', D.V.M.', '')
            tmpName = tmpName.replace(', Dvm', '')
            tmpName = tmpName.replace(', DVM', '')
            tmpName = tmpName.replace(', D. M. V.', '')
            tmpName = tmpName.replace(', Dmvv', '')
            tmpName = tmpName.replace(', D.V.M.', '')
            tmpName = tmpName.replace(',D.V.M.', '')

            tmpName = tmpName.replace(', Vmd', '')
            tmpName = tmpName.replace(', V.M.D', '')
            tmpName = tmpName.replace(', Vm', '')

    except AttributeError as ae:
        tmpName = "**NO NAME**"

    tmpName = tmpName.strip()
    splitName = tmpName.split(' ')
    if len(splitName) == 1:
        firstName = ''
        middleName = ''
        lastName = splitName[0]
    elif len(splitName) == 2:
        firstName = splitName[0]
        middleName = ''
        lastName = splitName[1]
    elif len(splitName) == 3:
        firstName = splitName[0]
        middleName = splitName[1]
        lastName = splitName[2]
    else:
        firstName = ''
        middleName = ''
        lastName = '**COMPLEX NAME**'

    firstName = firstName.strip()
    middleName = middleName.strip()
    lastName = lastName.strip()

    firstName = firstName.replace('.', '')
    middleName = middleName.replace('.', '')
    lastName = lastName.replace('.', '')

    return {'firstName': firstName, 'middleName': middleName, 'lastName': lastName}


def extract(fileName:str) -> pd.DataFrame:
    data = pd.read_csv(fileName)
    df = pd.DataFrame(data)
    # Because we don't like NaN and would rather deal
    # with it one time!
    df1 = df.replace(np.nan, '', regex=True)
    return df1


def transform(data: pd.DataFrame, verbose: str) -> pd.DataFrame:
    hcps = HCPS(
        api_client_id=config.MEDPRO_API_CLIENT_ID,
        api_client_secret=config.MEDPRO_API_CLIENT_SECRET,
        auth_token=token_check(config.CLIENT_TOKEN_FILENAME,
                               config.MEDPRO_API_CLIENT_ID, 
                               config.MEDPRO_API_CLIENT_SECRET
                               )
    )

    universe = Universe(
        api_client_id=config.MEDPRO_API_CLIENT_ID,
        api_client_secret=config.MEDPRO_API_CLIENT_SECRET,
        auth_token=token_check(config.CLIENT_TOKEN_FILENAME,
                               config.MEDPRO_API_CLIENT_ID, 
                               config.MEDPRO_API_CLIENT_SECRET
                               )
    )

    transformed = []
    if verbose.upper() == 'Y':
        print(" ")
        print_progress_bar(0, len(data), prefix='Progress:', suffix="Complete", length=40)
    for index, row in data.iterrows():
        parsedName = clean_and_parse_name(row["vetname"])
        vetMedproId = ''
        vetMedproState = ''
        vetInUniverse = ''
        vetMedproLicense = ''
        vetMedproLicenseStatus = ''
        vetMedproLicenseReceived = ''
        vetMedproLicenseExpires = ''

        # First search MedPro using the state we 
        # have for the vet.
        rv = hcps.search(stateOfLicense=row["license_state_cd"], 
                        lastName=parsedName["lastName"], 
                        firstName=parsedName["firstName"], 
                        middleName=parsedName["middleName"]
                        )

        if len(rv) == 1:
            vetMedproId = rv[0].get('medProID','')
            vetMedproState = rv[0].get('stateLicenseInfo_LicenseState', '')
            vetInUniverse = rv[0].get('customerData_InUniverse', '')
            vetMedproLicense = rv[0].get('stateLicense_StateLicenseNumber', '')
            vetMedproLicenseStatus = rv[0].get('stateLicense_Sampleability_OverallSampleability', '')
            vetMedproLicenseReceived = rv[0].get('stateLicense_Sampleability_LastReceivedDate', '')
            vetMedproLicenseExpires = rv[0].get('stateLicense_AdjustedExpirationDate', '')

            if vetInUniverse is False:
                universe.addToUniverse(medpro_id=vetMedproId, 
                                        client_id=row["kyriosvetid"]
                                        )

        transformed.append({
            "Kyrios ID": row["kyriosvetid"],
            "Full Name": row["vetname"].strip(),
            "License #": row["license_num"],
            "License State": row["license_state_cd"],
            "First Name": parsedName['firstName'].strip(),
            "Middle Name": parsedName['middleName'].strip(),
            "Last Name": parsedName['lastName'].strip(),
            "MedPro Result Count": len(rv),
            "MedPro ID": vetMedproId,
            "MedPro State": vetMedproState,
            "MedPro In Universe": vetInUniverse,
            "MedPro License": vetMedproLicense,
            "MedPro LicenseStatus": vetMedproLicenseStatus,
            "MedPro License Received": vetMedproLicenseReceived,
            "MedPro License Expires": vetMedproLicenseExpires

        })

        if verbose.upper() == 'Y':
            print_progress_bar(index, len(data), prefix='Progress:', suffix="Complete", length=40)

    transformedDataFrame =  pd.DataFrame(transformed)
    return transformedDataFrame.sort_values(by='MedPro Result Count', ascending=True)

def load(data:pd.DataFrame, path: str) -> None:
    data.to_csv(path_or_buf=path, index=False)

@click.command()
@click.option('-f',  '--infile', help='Input file to process',type=str)
@click.option('-o',  '--outfile', default='results', help='Output file',type=str)
@click.option('-v',  '--verbose', default='N', help='Show detailed progress',type=str)
def process(infile: str, outfile: str, verbose: str) -> None:  
    startTime = int(time.time())

    verifiedVets = extract(infile)
    transformedVets = transform(verifiedVets, verbose)
    load(data=transformedVets, path=f'{outfile}_{int(datetime.datetime.now().timestamp())}.csv')

    elapsedTime = int(time.time()) - startTime
    elapsedTimeStr = str(datetime.timedelta(seconds=elapsedTime))
    print(f"\nElapsed Time: {elapsedTimeStr}")


if __name__ == '__main__':
    check_version()
    process()
