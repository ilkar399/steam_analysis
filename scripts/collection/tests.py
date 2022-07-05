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
    # Downloading application list
    try:
        full_ids = applist.get_app_list()
        full_ids.to_csv(f'{download_path}full_steam_ids.csv', index=False)
    except Exception as e:
        if (verbose):
            print(e)
        return False
    # Checking the downloaded application list
    full_ids = pd.read_csv(f'{download_path}full_steam_ids.csv')
    row_count = full_ids.shape[0]
    ids_count = full_ids.drop_duplicates(subset='download_appid', keep='last').shape[0]
    last_modified_na = full_ids.last_modified.isna().sum()
    price_change_na = full_ids.price_change_number.isna().sum()
    if (verbose):
        print(f'Application IDs: {ids_count}')
        print(f'Null last modified: {last_modified_na}')
        print(f'Null price change: {price_change_na}')
    if (ids_count < 10000):
        return False
    return True

def all(verbose = False):
    # App list download
    if (get_app_list(verbose)):
        print('App list download test PASSED')
    else:
        print('App list download test FAILED')
    # Steam apps download

    # SteamSpy apps download

    # Steam Reviews download
    return True

all(verbose = True)