"""
Common data collection functions
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

def get_api_key():
    """Return the Steam dev API key from _credentials

    Parameters
    ----------
    none

    Returns
    -------
    api_key
        String containing Steam dev API key. Empty if none parsed.
    """
    try:
        with open('./data/_credentials/steam_key.txt') as f:
            api_key = f.read()
    except:
        raise("Error getting API Key")
    return api_key

def get_proxies():
    """Return the dictionary of proxies from _credentials

    Parameters
    ----------
    none

    Returns
    -------
    proxies
        dictionary of proxies. None if none parsed
    """
    try:
        with open('./data/_credentials/proxies.txt', 'r') as f:
            proxies = eval(f.read())
        if not isinstance(proxies, dict):
            proxies = None
    except:
        proxies = None
    return proxies

def get_download_path():
    return './scripts/temp/'

def get_request(url, parameters=None, steamspy=False, proxies = None):
    """Return json-formatted response of a get request using optional parameters.
    
    Parameters
    ----------
    url : string
    parameters : {'parameter': 'value'}
        parameters to pass as part of get request
    steamspy: boolean
        request processing for SteamSpy
    proxies: {'protocol': 'connection_string'}
        dictionary conntaining proxies to be used with the request
    
    Returns
    -------
    json_data
        json-formatted response (dict-like)
    """
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get(url=url, params=parameters, headers = headers, proxies = proxies)
    except requests.exceptions.SSLError as s:
        print('SSL Error:', s)
        
        for i in range(5, 0, -1):
            print('\rWaiting... ({})'.format(i), end='')
            time.sleep(1)
        print('\rRetrying.' + ' '*10)
        
        # recursively try again
        return get_request(url, parameters, steamspy, proxies)
    
    if response:
        return response.json()
    else:
        # We do not know how many pages steamspy has... and it seems to work well, so we will use no response to stop.
        if steamspy:
            return 'stop'
        else :
            # response is none usually means too many requests. Wait and try again 
            print('No response, waiting 15 seconds...')
            time.sleep(15)
            print('Retrying.')
            return get_request(url, parameters, steamspy) 

"""
Indexes
"""

def reset_index(download_path, index_filename):
    """
    Reset index in file to 0.

    Parameters
    ----------
    download_path : string
    index_filename : string

    Returns
    -------
    none
    """
    rel_path = os.path.join(download_path, index_filename)
    
    f = open(rel_path, 'w')
    f.write('0')
        

def get_index(download_path, index_filename):
    """
    Retrieve index from file, returning 0 if file not found.

    Parameters
    ----------
    download_path : string
    index_filename : string
    Returns
    -------
    integer
        index written in the first line of the index_filename.
        0 if error
    """
    try:
        rel_path = os.path.join(download_path, index_filename)
        with open(rel_path, 'r') as f:
            index = int(f.readline())
            #This just reads the initial line
    
    except FileNotFoundError:
        index = 0
        
    return index


def prepare_data_file(download_path, filename, index, columns):
    """
    Create file and write headers if index is 0.

    Parameters
    ----------
    download_path : string
    index_filename : string

    Returns
    -------
    none
    """
    if index == 0:
        rel_path = os.path.join(download_path, filename)

        with open(rel_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()


"""
App Data
"""
def get_app_data(app_list, start, stop, parser, pause, errors_list,
                 download_appid = False, last_modified = False):
    """Return list of app data generated from parser.
    
    Parameters
    ----------
    app_list : dataframe of appid and name
    start : starting index in app_list slice
    stop : ending index in app_list slice
    parser : custom function to format request
    pause : time to wait after each api request
    errors_list : list to store appid errors
    
    Keyword arguments
    -----------------
    download_appid : add id from app_list for the downloaded app
    last_modified : add last_modified for the downloaded app
    
    Returns
    -------
    list with application data
    """
    app_data = []
    # iterate through each row of app_list, confined by start and stop
    for index, row in app_list[start:stop].iterrows():
        print('Current index: {}'.format(index), end='\r')

        # retrive app data for a row, handled by supplied parser, and append to list
        try:
            data = parser(row['download_appid'])
        except Exception as ex:
            errors_list.append(row['download_appid'])
            print('\nError getting data for {} with exception {}\n'.format(row['download_appid'], type(ex).__name__))
        if download_appid:
            data['download_appid'] = row['download_appid']
        if last_modified:
            data['last_modified'] = row['last_modified']
        app_data.append(data)

        time.sleep(pause) # prevent overloading api with requests

    return app_data


def process_batches(parser, app_list, download_path, data_filename, index_filename,
                    errors_list, columns,
                    begin=0, end=-1, batchsize=100, pause=1,
                    download_appid = False, last_modified = False):
    """Process app data in batches, writing directly to file.
    
    
    Parameters
    ----------
    parser : custom function to format request
    app_list : dataframe of appid and name
    download_path : path to store data
    data_filename : filename to save app data
    index_filename : filename to store highest index written
    errors_list : list to store appid errors
    columns : column names for file
    
    Keyword arguments
    -----------------
    begin : starting index (get from index_filename, default 0)
    end : index to finish (defaults to end of app_list)
    batchsize : number of apps to write in each batch (default 100)
    pause : time to wait after each api request (defualt 1)
    download_appid : add id from app_list for the downloaded app
    last_modified : add last_modified for the downloaded app
    
    Returns
    -------
    none
    """
    print('Starting at index {}:\n'.format(begin))
    
    # by default, process all apps in app_list
    if end == -1:
        end = len(app_list) + 1
    
    # generate array of batch begin and end points
    batches = np.arange(begin, end, batchsize)
    batches = np.append(batches, end)
    
    apps_written = 0
    batch_times = []
    
    for i in range(len(batches) - 1):
        start_time = time.time()
        
        start = batches[i]
        stop = batches[i+1]
        
        app_data = get_app_data(app_list, start, stop, parser, pause, errors_list, download_appid, last_modified)
        
        rel_path = os.path.join(download_path, data_filename)
        
        # writing app data to file
        with open(rel_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
            
            for j in range(3,0,-1):
                print("\rAbout to write data, don't stop script! ({})".format(j), end='')
                time.sleep(0.5)
            
            writer.writerows(app_data)
            print('\rExported lines {}-{} to {}.'.format(start, stop-1, data_filename), end=' ')
            
        apps_written += len(app_data)
        
        idx_path = os.path.join(download_path, index_filename)
        
        # writing last index to file
        with open(idx_path, 'w') as f:
            index = stop
            print(index, file=f)
            
        # logging time taken
        end_time = time.time()
        time_taken = end_time - start_time
        
        batch_times.append(time_taken)
        mean_time = statistics.mean(batch_times)
        
        est_remaining = (len(batches) - i - 2) * mean_time
        
        remaining_td = dt.timedelta(seconds=round(est_remaining))
        time_td = dt.timedelta(seconds=round(time_taken))
        mean_td = dt.timedelta(seconds=round(mean_time))
        
        print('Batch {} time: {} (avg: {}, remaining: {})'.format(i, time_td, mean_td, remaining_td))
            
    print('\nProcessing batches complete. {} apps written'.format(apps_written))