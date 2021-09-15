import datetime
import openpyxl
import os
import pandas as pd
import sys
from termcolor import colored

def dir_exists(target:str) -> bool:
    return os.path.isdir(target)
    
def time_stamp(msg:str, color='white') -> None:
    dt = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    msg = colored(f"{dt}\t{msg}", color)
    print(msg, flush=True)

def check_version() -> None:
    if not sys.version_info > (2, 7):
        time_stamp("You are running a version of Python that's over 10 years old! Please upgrade to Python3!", color="red")
        exit()
    elif not sys.version_info  >= (3, 6):
        time_stamp("Please upgrade to at least Python 3.6.")
        exit()
        
def commafy(n):
    return "{:,}".format(n)

# Print iterations progress
def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    if total > 0:
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
        # Print New Line on Complete
        if iteration == total:
            print()


def get_csv_data(fileName):
    data = pd.read_csv(fileName)
    df = pd.DataFrame(data)
    return df

def get_excel_data(fileName, sheetName):
    data = pd.read_excel(fileName, sheetName)
    df = pd.DataFrame(data)
    return df

def update_excel_data(fileName, sheetName, cell, value):
    workbook = openpyxl.load_workbook(fileName)
    worksheet = workbook.get_sheet_by_name(sheetName)
    worksheet[cell] = value
    workbook.save(fileName)
    workbook.close()

