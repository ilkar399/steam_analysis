"""
Collection tests
"""

# standart library imports

# third party imports
import pandas as pd
import requests
import requests.auth
# project imports
import applist
import common

download_path = './scripts/test/'

def get_app_list(verbose = False):
    """
    Testing getting application list
    """
    try:
        full_ids = applist.get_app_list()
        full_ids.to_csv(f'{download_path}full_steam_ids.csv', index=False)
    except Exception as e:
        if (verbose):
            print(e)
        return False
    return True

def all(verbose = False):
    get_app_list()
    return True

all()