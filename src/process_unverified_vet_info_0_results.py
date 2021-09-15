import os
import click
import datetime
import pandas as pd
import time

import common.config as config
from common.MedPro.hcps import HCPS
from common.MedPro.utils import token_check
from common.utils import get_excel_data 

vetExcelFile = 'UnverifiedVetInfo_Results.xlsx'
resultsFilename = 'UnverifiedVetInfo_Results_0.txt'


@click.command()
@click.option('-v',  '--verbose', default='N', help='Show detailed progress',type=str)
def process(verbose):  
    startTime = int(time.time())

    hcps = HCPS(
        api_client_id=config.MEDPRO_API_CLIENT_ID,
        api_client_secret=config.MEDPRO_API_CLIENT_SECRET,
        auth_token=token_check(config.CLIENT_TOKEN_FILENAME,
                               config.MEDPRO_API_CLIENT_ID, 
                               config.MEDPRO_API_CLIENT_SECRET
                               )
    )

    df = get_excel_data(vetExcelFile,"Unverified - Results")
    totalRows = len(df.index)
    totalProcessed = 0
    for index, row in df.iterrows():
        if verbose.upper() == 'Y':
            print(f"Processing: {index} of {totalRows}")

        if int(row['# MedPro Responses']) == 0:
            kyriosID = row['Kyrios ID']
            if type(row['First']) == str:
                firstName = row['First']
            else:
                firstName = ''

            if type(row['Middle']) == str:
                middleName = row['Middle']
            else:
                middleName = ''

            if type(row['Last']) == str:
                lastName = row['Last']
            else:
                lastName = ''

            if type(row['Vet State']) == str:
                vetState = row['Vet State']
            else:
                vetState = ''

            if type(row['Clinic State']) == str:
                clinicState = row['Clinic State']
            else:
                clinicState = ''

            licenseNum = row['License #']
            # Let me know if I've switched first/last name

            flippedNames = False
            rv0 = rv1 = rv2 = rv3 = []

            # If the clinicState and vetState are equal,
            # only query with the first,last switched saving
            # 2 api calls
            if clinicState == vetState:
                rv0 = hcps.search(stateOfLicense=vetState, 
                                lastName=lastName, 
                                firstName=firstName
                                )
                if len(rv0) == 0:
                    flippedNames = True
                    rv2 = hcps.search(stateOfLicense=vetState, 
                                    lastName=firstName, 
                                    firstName=lastName
                                    )
            else:
                # First Name - Last Name
                rv0 = hcps.search(stateOfLicense=vetState, 
                                lastName=lastName, 
                                firstName=firstName
                                )
                if len(rv0) == 0:
                    rv1 = hcps.search(stateOfLicense=clinicState, 
                                    lastName=lastName, 
                                    firstName=firstName
                                    )

                    if len(rv1) == 0:
                        flippedNames = True
                        # Last Name - First Name
                        rv2 = hcps.search(stateOfLicense=vetState, 
                                        lastName=firstName, 
                                        firstName=lastName
                                        )
                        if len(rv2) == 0:
                            rv3 = hcps.search(stateOfLicense=clinicState, 
                                            lastName=firstName, 
                                            firstName=lastName
                                            )

            if len(rv0) != 0 or \
               len(rv1) != 0 or \
               len(rv2) != 0 or \
               len(rv3) != 0:

                if len(rv0) == 1:
                    vetMedproId = rv0[0].get('medProID','')
                    vetMedproState = rv0[0].get('stateLicenseInfo_LicenseState', '')
                    vetInUniverse = rv0[0].get('customerData_InUniverse', '')
                    vetMedproLicense = rv0[0].get('stateLicense_StateLicenseNumber', '')
                    vetMedproLicenseStatus = rv0[0].get('stateLicense_Sampleability_OverallSampleability', '')
                else:
                    vetMedproId = ''
                    vetMedproState = ''
                    vetInUniverse = ''
                    vetMedproLicense = ''
                    vetMedproLicenseStatus = ''

                numResponses = len(rv0)+len(rv1)+len(rv2)+len(rv3)
                if verbose.upper() == 'Y':
                    print(f"Index: {index}")
                    print(f"Kyrios ID: {kyriosID}")
                    print(f"Full Name: {row['Full Name']}")

                    if flippedNames is True:
                        print(f"First Name: {lastName}")
                        print(f"Middle Name: {middleName}")
                        print(f"Last Name: {firstName}")
                    else:
                        print(f"First Name: {firstName}")
                        print(f"Middle Name: {middleName}")
                        print(f"Last Name: {lastName}")

                    print(f"License #: {licenseNum}")
                    print(f"Vet State: {vetState}")
                    print(f"Clinic State: {clinicState}")
                    # print(f"Queries: {len(rv0)}\t{len(rv1)}\t{len(rv2)}\t{len(rv3)}\t")
                    print(f"# MedPro Responses:\t{numResponses}")
                    print(f"MedPro ID: \t{vetMedproId}")
                    print(f"MedPro State: \t{vetMedproState}")
                    print(f"In Universe: \t{vetInUniverse}")
                    print(f"MedPro License: \t{vetMedproLicense}")
                    print(f"MedPro license Status: {vetMedproLicenseStatus}")
                    print(" ")

                with open(resultsFilename, 'a+') as outFile:
                    outFile.write(f"{kyriosID}")
                    outFile.write(f"!{row['Full Name']}")

                    if flippedNames is True:
                        outFile.write(f"!{lastName}")
                        outFile.write(f"!{middleName}")
                        outFile.write(f"!{firstName}")
                    else:
                        outFile.write(f"!{firstName}")
                        outFile.write(f"!{middleName}")
                        outFile.write(f"!{lastName}")

                    outFile.write(f"!{licenseNum}")
                    outFile.write(f"!{vetState}")
                    outFile.write(f"!{clinicState}")
                    outFile.write(f"!{numResponses}")
                    outFile.write(f"!{vetMedproId}")
                    outFile.write(f"!{vetMedproState}")
                    outFile.write(f"!{vetInUniverse}")
                    outFile.write(f"!{vetMedproLicense}")
                    outFile.write(f"!{vetMedproLicenseStatus}")
                    outFile.write("\n")
                    outFile.flush()


            totalProcessed += 1

    print(totalProcessed)

    elapsedTime = int(time.time()) - startTime
    elapsedTimeStr = str(datetime.timedelta(seconds=elapsedTime))
    print(f"Elapsed Time: {elapsedTimeStr}")

if __name__ == '__main__':  
    process()
