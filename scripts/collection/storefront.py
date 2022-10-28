"""
Functions to get the Application data from Steam Storefront
"""

# standard library imports
import csv
import datetime as dt
import json
import os
import statistics
import time

# third-party imports
import numpy as np
import pandas as pd
import requests
import requests.auth

# project imports
import common
import applist

APIKey = common.get_api_key()
proxies = common.get_proxies()

def parse_steam_request(appid):
    """
    Unique parser to handle data from Steam Store API.
    
    Parameters
    ----------
    appid : application ID

    Returns
    -------
    json formatted data (dict-like)
    """
    url = 'http://store.steampowered.com/api/appdetails/'
    parameters = {'appids': appid, 'key': APIKey}
    
    json_data = common.get_request(url, parameters=parameters, proxies=proxies)
    json_app_data = json_data[str(appid)]
    
    if json_app_data['success']:
        data = json_app_data['data']
    else:
        data = {'steam_appid': appid}
        
    return data


def download_storefront(download_path, full_download = True, refresh_ids = False, verbose = False):
    """
    Download data for Steam storefront

    Parameters
    ----------
    download_path : the path where the data is downloaded to (and 'full_steam_ids.csv' is located)

    Keyword arguments
    -----------------
    full_download : download all apps available in ids table, default to True
    refresh_ids : refresh the ids table, default to False
    verbose : verbose output, default to False

    Returns
    -------
    bool :
        True if no errors, False if errors raised
    """
    steam_app_data = 'steam_app_data.csv'
    steam_app_data_delta = 'steam_app_data_delta.csv'
    steam_index = 'steam_index.txt'

    steam_columns = [
        'type', 'name', 'steam_appid', 'required_age', 'is_free', 'controller_support',
        'dlc', 'detailed_description', 'about_the_game', 'short_description', 'fullgame',
        'supported_languages', 'header_image', 'website', 'pc_requirements', 'mac_requirements',
        'linux_requirements', 'legal_notice', 'drm_notice', 'ext_user_account_notice',
        'developers', 'publishers', 'demos', 'price_overview', 'packages', 'package_groups',
        'platforms', 'metacritic', 'reviews', 'categories', 'genres', 'screenshots',
        'movies', 'recommendations', 'achievements', 'release_date', 'support_info',
        'background', 'content_descriptors',
        'download_appid', 'last_modified'
    ]

    steam_errors = []

    # Redownload IDs
    if (refresh_ids):
        # Here we get the list of appids from steam
        full_steam_ids = applist.get_app_list()
        full_download = True
    else:
        full_steam_ids = pd.read_csv(f'{download_path}full_steam_ids.csv')

    if (os.path.isfile(download_path+steam_app_data_delta) == False) or (full_download):
        # Download all apps
        common.reset_index(download_path, steam_index)
        index = 0
    else:
        # Retrieve last index downloaded from file
        index = common.get_index(download_path, steam_index)
        
    # Wipe or create data file and write headers if no previous file present
    if (os.path.isfile(download_path+steam_app_data) == False):
        common.prepare_data_file(download_path, steam_app_data, index, steam_columns)
        
    # Wipe or create data file delta and write headers if index is 0
    if (os.path.isfile(download_path+steam_app_data_delta) == False) or (index == 0):
        common.prepare_data_file(download_path, steam_app_data_delta, 0, steam_columns)
              
    # Here we get the real list of ids not yet in our dataframe. If this is the first time we are downloading the data, we can skip
    # This step and instead use the full app_list.
    try:
        oldlist = pd.read_csv('../data/download/steam_app_data.csv', usecols = ['name','download_appid'])
        steam_ids = applist.get_update_ids(full_steam_ids, oldlist)
    except FileNotFoundError:
        print('Pre-existing file not found. Downloading data for all IDs\n')
        steam_ids = full_steam_ids

    # I separated the long process to be able to debug it better.
    # Set end and chunksize for demonstration - remove to run through entire app list
    # Here by default we passed "app_list" that contained all the information and saved it, now we will modify it a bit
    # And add pre-processing and post-processing
    print(f'Adding {str(len(steam_ids))} new ids.\n')

    # Adding download start timestamp
    log_time = []
    log_time.append(['Storefront download start', time.time()])

    # Downloadidng in batches to the delta file
    common.process_batches(
        parser=parse_steam_request,
        app_list=steam_ids,
        download_path=download_path,
        data_filename=steam_app_data_delta,
        index_filename=steam_index,
        errors_list=steam_errors,
        columns=steam_columns,
        begin=index,
        #pause=0.5
        batchsize=100,
        pause=1,
        download_appid = True,
        last_modified = True
    )

    log_time.append(['Storefront download end', time.time()])

    # Saving the file, making a backup first
    try:
        oldlist = pd.read_csv('../data/download/steam_app_data.csv')
        # We change the old file to backup, so remove any backup named this way before...
        os.replace('../data/download/steam_app_data.csv', '../data/download/steam_app_data_backup.csv')
        newlist = pd.read_csv('../data/download/steam_app_data_delta.csv')
        oldlist = oldlist.append(newlist, ignore_index=True)
        oldlist.to_csv('../data/download/steam_app_data.csv', index=False)
    except FileNotFoundError:
        os.rename('../data/download/steam_app_data_delta.csv', '../data/download/steam_app_data.csv')

    # Removing downloaded duplicates, keeping only the last one
    steam_app_data = steam_app_data.drop_duplicates(subset='download_appid', keep='last')
    steam_app_data.to_csv('../data/download/steam_app_data.csv', index=False)

    # Saving errors and download times
    steam_errors_df = pd.DataFrame(steam_errors, columns=['appid'])
    steam_errors_df.to_csv('../data/download/steam_errors.csv', index=False)

    log_columns = ['operation', 'timestamp']
    try:
        log_df = pd.read_csv('../data/download/download_log.csv', header=0)
    except:
        log_df = pd.DataFrame(columns=log_columns)

    log_df = log_df.append(pd.DataFrame(columns=log_columns, data=log_time), ignore_index=True)
    log_df.to_csv('../data/download/download_log.csv', index=False)
    return True