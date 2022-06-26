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

def getAppListBatch(url, parameters):
    """
    Getting application list data in batches, since IStoreService
    has limited max output
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

def getAppList():
    """
    Getting the list of applications using Steam IStoreService
    Use https://steamapi.xpaw.me/#IStoreService/GetAppInfo as a reference
    for additional parameters
    
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
        more_results, steam_ids, last_appid = getAppListBatch(url, parameters)
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
    Getting a table of apps that we are to download by comparing:
    
    new_list : table of apps from IStoreService,
    old_list : table of available apps. Requires to have 'download_appid' column
    
    """
    #We are going to forget about names and only care about IDs.
    old_list = old_list[['download_appid']]
    updated_list = new_list[~new_list['download_appid'].isin(old_list['download_appid'])].copy().drop_duplicates().reset_index(drop=True)
    return updated_list