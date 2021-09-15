import os
import datetime
import time

import common.config as config
from common.utils import get_excel_data, get_csv_data, time_stamp
 
vetExcelFile = 'KS_Currently_Licensed.xlsx'
vetCSVFile = 'KS_Kyrios_License_Data.csv'
vetTxtFile = 'KS_Kyrios_License_Mapped_Data.txt'

# Load the KS vet license data
licensesDataFrame = get_excel_data(vetExcelFile, "Sheet1")

def split_name(fullName):
    tmpNames = fullName.split(' ')
    if len(tmpNames) == 2:
        return tmpNames[0].strip(), tmpNames[1].strip()
    elif len(tmpNames) == 3:
        return tmpNames[0].strip(), tmpNames[2].strip()
    else:
        print(tmpNames)
        exit()

def get_license_number(firstName, lastName):

    licenseNumber = 'NOT_FOUND'
    for index, row in licensesDataFrame.iterrows():
        try:        
            licenseFirstName = f"{row['First Name']}".lower()
            licenseLastName = f"{row['Last Name']}".lower()
            if licenseFirstName == firstName.lower() and licenseLastName == lastName.lower():
                licenseNumber = int(row['ID Status'])
        except ValueError as ve:
            pass
    return licenseNumber

def process():  
    startTime = int(time.time())

    # "kyriosid","vet_nm","medproid","license_num","license_state_cd"

    df = get_csv_data(vetCSVFile)
    totalRows = len(df.index)
    cntFound = 0
    cntNotFound = 0
    for index, row in df.iterrows():
        try:        
            kyriosID = int(row['kyriosid'])
            medproID = int(row['medproid'])
            vetFirstName, vetLastName = split_name(row['vet_nm'])
            licenseNumber = get_license_number(vetFirstName, vetLastName)
            if licenseNumber == "NOT_FOUND":
                cntNotFound += 1
            else:
                cntFound += 1
            with open(vetTxtFile, 'a+') as outFile:
                line = f"{kyriosID}!{medproID}!{vetFirstName}!{vetLastName}!{licenseNumber}\n"
                outFile.write(line)
        except ValueError as ve:
            pass

    elapsedTime = int(time.time()) - startTime
    elapsedTimeStr = str(datetime.timedelta(seconds=elapsedTime))
    time_stamp(f"Total Rows: {totalRows}")
    time_stamp(f"Found: {cntFound}")
    time_stamp(f"Not Found: {cntNotFound}")
    time_stamp(f"Elapsed Time: {elapsedTimeStr}")

if __name__ == '__main__':  
    process()
