import os
import click
import datetime
import json
import re
import time

import common.config as config
from common.MedPro.hcps import HCPS
from common.MedPro.utils import token_check
   
vetsImportFile = 'RemainingVerifiedVetsWithoutMedproIDs.7.22.csv'
vetsImportFileResults = 'RemainingVerifiedVetsWithoutMedproIDsResults.7.22.csv'
unverifiedVetInfoBucketFile = "RemainingVerifiedVetsWithoutMedproIDsBuckets.7.22.csv"

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


@click.command()
@click.option('-v',  '--verbose', default='N', help='Show detailed progress',type=str)
def process(verbose):  
    startTime = int(time.time())
    buckets = {}
    kyriosVetIdPos = 0
    vetNmPos = 1
    licenseNumPos = 2
    licenseStateCdPos = 3

    hcps = HCPS(
        api_client_id=config.MEDPRO_API_CLIENT_ID,
        api_client_secret=config.MEDPRO_API_CLIENT_SECRET,
        auth_token=token_check(config.CLIENT_TOKEN_FILENAME,
                               config.MEDPRO_API_CLIENT_ID, 
                               config.MEDPRO_API_CLIENT_SECRET
                               )
    )

    # Using readlines()
    file1 = open(vetsImportFile, 'r')
    vets = file1.readlines()

    headerLine = "Kyrios ID!Full Name!First!Middle!Last!License #!Vet State!# MedPro Responses!MedPro ID!MedPro State!In Universe!MedPro License!MedPro License Status!MedPro License Received!MedPro License Expires\n"

    with open(vetsImportFileResults, "w") as outFile:
        outFile.write(headerLine)
        totalVets = len(vets)
        currentVet = 0
        for line in vets:
            currentVet += 1
            row = line.split(',')

            if len(row) >= 4:
                try:
                    kyriosID = row[kyriosVetIdPos]
                    fullName = row[vetNmPos].replace('"','')
                    vetFirstName = clean_and_parse_name(row[vetNmPos])['firstName']
                    vetMiddleName = clean_and_parse_name(row[vetNmPos])['middleName']
                    vetLastName = clean_and_parse_name(row[vetNmPos])['lastName']
                    vetState = row[licenseStateCdPos].strip()
                    vetLicenseNum = row[licenseNumPos].strip().replace('"', '')
                    if vetState == 'UNK':
                        vetState = ''

                    # First search MedPro using the state we 
                    # have for the vet.
                    rv = hcps.search(stateOfLicense=vetState, 
                                    lastName=vetLastName, 
                                    firstName=vetFirstName, 
                                    middleName=vetMiddleName
                                    )
                    
                    if len(rv) == 1:
                        vetMedproId = rv[0].get('medProID','')
                        vetMedproState = rv[0].get('stateLicenseInfo_LicenseState', '')
                        vetInUniverse = rv[0].get('customerData_InUniverse', '')
                        vetMedproLicense = rv[0].get('stateLicense_StateLicenseNumber', '')
                        vetMedproLicenseStatus = rv[0].get('stateLicense_Sampleability_OverallSampleability', '')
                        vetMedproLicenseReceived = rv[0].get('stateLicense_Sampleability_LastReceivedDate', '')
                        vetMedproLicenseExpires = rv[0].get('stateLicense_AdjustedExpirationDate', '')
                    else:
                        vetMedproId = ''
                        vetMedproState = ''
                        vetInUniverse = ''
                        vetMedproLicense = ''
                        vetMedproLicenseStatus = ''
                        vetMedproLicenseReceived = ''
                        vetMedproLicenseExpires = ''

                    if verbose.upper() == 'Y':
                        print(f"Progress: {currentVet} / {totalVets}")            
                        print(f"Kyrios ID: {kyriosID}")
                        print(f"Full Name: {fullName}")
                        print(f"First:\t{vetFirstName}")
                        print(f"Middle:\t{vetMiddleName}")
                        print(f"Last:\t{vetLastName}")
                        print(f"License #:\t{vetLicenseNum}")
                        print(f"Vet State:\t{vetState}")
                        print(f"# MedPro Responses:\t{len(rv)}")
                        print(f"MedPro ID: \t{vetMedproId}")
                        print(f"MedPro State: \t{vetMedproState}")
                        print(f"In Universe: \t{vetInUniverse}")
                        print(f"MedPro License: \t{vetMedproLicense}")
                        print(f"MedPro license Status: {vetMedproLicenseStatus}")
                        print(f"MedPro license received: {vetMedproLicenseReceived}")
                        print(f"MedPro license expires: {vetMedproLicenseExpires}")
                        print(" ")

                    size = f"{len(rv)}"
                    if size in buckets.keys():
                        buckets[size] += 1
                    else:
                        buckets[size] = 1
                    
                    if len(rv) == 1:
                        dataLine = f"{kyriosID}!{fullName}!{vetFirstName}!{vetMiddleName}!{vetLastName}!{vetLicenseNum}!{vetState}!{len(rv)}!{vetMedproId}!{vetMedproState}!{vetInUniverse}!{vetMedproLicense}!{vetMedproLicenseStatus}!{vetMedproLicenseReceived}!{vetMedproLicenseExpires}\n"
                        outFile.write(dataLine)
                        outFile.flush()

                except IndexError as ie:
                    print('*************** ')
                    print(line)
                    exit()

    elapsedTime = int(time.time()) - startTime
    elapsedTimeStr = str(datetime.timedelta(seconds=elapsedTime))
    print(f"Elapsed Time: {elapsedTimeStr}")

    with open(unverifiedVetInfoBucketFile, "w") as bf:
        for k in buckets.keys():
            bf.write(f"{k}!{buckets[k]}\n")


if __name__ == '__main__':  
    process()
