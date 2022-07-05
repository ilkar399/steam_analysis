"""
Functions to get the list of Applications for data collection
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

def get_app_list_batch(url, parameters):
    """
    Getting application list data in batches, since IStoreService
    has limited max output

    Parameters
    ----------
    url : string
    parameters : dictionary of the request parameters

    Returns
    -------
    more_results : boolean
        have more results left
    steam_id : data in dataframe:
        Example of a single app data:
        "appid":10,"name":"Counter-Strike","last_modified":1602535893,"price_change_number":13853601
    last_appid : last application id in the batch
    """
    proxies = common.get_proxies()
    json_data = common.get_request(
        url,
        parameters=parameters,
        proxies = proxies
        )
    steam_id = pd.DataFrame.from_dict(json_data['response']['apps'])
    try:
        more_results = json_data['response']['have_more_results']
        last_appid =  json_data['response']['last_appid']
    except:
        more_results = False
        last_appid = False
    return more_results, steam_id, last_appid

def get_app_list():
    """
    Getting the list of applications using Steam IStoreService
    Use https://steamapi.xpaw.me/#IStoreService/GetAppInfo as a reference
    for additional parameters 

    Parameters
    ----------
    none

    Returns
    -------
    Application data in dataframe:
        Example of a single app data:
        "appid":10,"name":"Counter-Strike","last_modified":1602535893,"price_change_number":13853601
   
    """
    url = 'https://api.steampowered.com/IStoreService/GetAppList/v1/?'
    APIKey = common.get_api_key()
    parameters = {'key': APIKey,
                 'include_dlc': 'true'}
    more_results = True
    begin = True
    # from the request we get the more_results flag and also the last_appid, so we use them for the next requests.
    while (more_results):
        more_results, steam_ids, last_appid = get_app_list_batch(url, parameters)
        parameters['last_appid'] = last_appid
        if (begin):
            steam_allids = steam_ids
            begin = False
        else:
            steam_allids = steam_allids.append(steam_ids)
    steam_allids.rename(columns = {'appid': 'download_appid'}, inplace = True)
    return steam_allids.loc[:,['download_appid', 'last_modified', 'price_change_number']]

def get_update_ids(new_list, old_list):
    """
    Getting a dataframe of apps that we are to download by comparing:
    
    Parameters
    ----------
    new_list : dataframe of apps from IStoreService,
    old_list : dataframe of available apps. Requires to have 'download_appid' column

    Returns
    -------
    updated dataframe
    """
    #We are going to forget about names and only care about IDs.
    old_list = old_list[['download_appid']]
    updated_list = new_list[~new_list['download_appid'].isin(old_list['download_appid'])].copy().drop_duplicates().reset_index(drop=True)
    return updated_list

def download_app_list(download_path, verbose = False):
    """
    Downloading application list
    
    Parameters
    ----------
    download_path : the path where the data is downloaded to
    verbose : verbose output, default to False

    Returns
    -------
    bool
        True if success, False if Exception
   
    """
    try:
        full_ids = get_app_list()
        full_ids.to_csv(f'{download_path}full_steam_ids.csv', index=False)
    except Exception as e:
        if (verbose):
            print(e)
        return False
    if (verbose):
        print(f'Downloaded {full_ids.shape[0]} rows of data')
    return True