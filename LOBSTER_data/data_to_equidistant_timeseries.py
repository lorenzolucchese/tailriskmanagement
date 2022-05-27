# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 12:23:30 2020

@author: Lorenzo
"""
import os
import glob
import pandas as pd
import re
import datetime
import numpy as np
import pickle

nmin = 1
TICKER = 'SPY'

os.chdir(os.path.join('data', TICKER, TICKER+'_extracted_files'))

extension = 'csv'
dir_paths = os.listdir()
csv_file_list = []
output_path = os.path.join(os.path.pardir,TICKER +'_equidistant_log_returns')

#get a list of all subdirectories and search for csv files in these subdirectories

for dir_path in dir_paths:
    file_path = os.path.join(dir_path,'*.{}'.format(extension))
    csv_file_list_to_add = [i for i in glob.glob(file_path)]
    csv_file_list += csv_file_list_to_add


csv_orderbook = [name for name in csv_file_list if 'orderbook' in name]
csv_message   = [name for name in csv_file_list if 'message'   in name]

#check if exactly half of the files are orderbook and exactly half are messages
assert( len(csv_message) == len(csv_orderbook))
assert( len(csv_file_list) == len(csv_message) + len(csv_orderbook))

print('started loop')

orderbook_with_problems = []
messages_with_problems  = []
opening_closing_times = []
empty_time_intervals = []


for orderbook_name in csv_orderbook:
    
    print(orderbook_name)

    #read the orderbook. keep a record of problematic files
    try:
        df_orderbook = pd.read_csv(orderbook_name, header= None)
    except:
        orderbook_with_problems.append(orderbook_name)
        print('the following file has been skipped:  ' + orderbook_name)
        continue

    df_orderbook.columns = ("ASKp1" , "ASKs1" , "BIDp1",  "BIDs1")

    #get date first
    match = re.findall('\d{4}-\d{2}-\d{2}', orderbook_name)[-1]
    date = datetime.datetime.strptime(match, '%Y-%m-%d')

    #read times from message file. keep a record of problematic files
    message_name = orderbook_name.replace('orderbook','message')
    try:
        df_message  =  pd.read_csv(message_name, usecols = [0], header = None)
    except:
        messages_with_problems.append(message_name)
        print('the following file has been skipped:  ' + message_name)
        continue
    
    market_open = int(df_message.iloc[0]/60)/60 #open at minute before first transaction
    market_close = (int(df_message.iloc[-1]/60)+1)/60 #close at minute after last transaction
    
    #check that the two df have the same length
    assert (len(df_message) == len(df_orderbook))  

    #convert df_message.index to seconds since midnight and add this to the current date
    seconds_since_midnight = pd.to_timedelta(df_message[0], unit = 'S', errors="coerce")
    timeindex_ = seconds_since_midnight.values + pd.Series(date).repeat(repeats = len(seconds_since_midnight))
    
    # find the index of the last order in every n-minute batch (resampling) and
    # select the appropriate Bid-Ask prices and sizes from the orderbook
    df_indicestokeep = pd.DataFrame(range(len(df_message[0])), timeindex_)
    df_indices = df_indicestokeep.resample(str(nmin)+'min', closed='right').max()
    # keep track of the number of empty time intervals (on days that have at least one)
    if int(df_indices.isna().sum()) > 0:
        empty_time_intervals.append(str(date) + ' : ' + str(int(df_indices.isna().sum())))
    #add opening prices and fill in empty time intervals with preceding price
    indices = [0] + list(df_indices.ffill()[0])
    # reduce orderbook to relevant equidistant data (convert to numeric)
    df_orderbook_nmin = df_orderbook.iloc[indices]
    df_orderbook_nmin = df_orderbook_nmin.apply(pd.to_numeric)
    
    # compute the n-min equidistant microprices
    df_microprices =  (df_orderbook_nmin['ASKp1'] * df_orderbook_nmin['ASKs1'] + df_orderbook_nmin['BIDp1'] * df_orderbook_nmin['BIDs1']) / (df_orderbook_nmin['ASKs1'] + df_orderbook_nmin['BIDs1'])
    
    # label microprices with the appropriate time index and drop values outside of market hours
    market_open_minutes = range(int(market_open*60), int(market_close*60) + nmin, nmin)
    df_microprices.index = pd.to_timedelta(market_open_minutes, unit='m') + pd.Series(date).repeat(repeats = len(market_open_minutes))
    df_microprices = df_microprices.between_time(datetime.time(9, 30), datetime.time(16))
    
    #keep track of market opening and closing time if its not 9:30 - 16:00
    if not(market_open == 9.5 and market_close == 16):
        opening_closing_times.append(str(df_microprices.index[0]) + ' - ' + str(df_microprices.index[-1]))
    
    #compute n-min log returns
    log_returns_nmin = (np.log(df_microprices)).diff(1).drop(df_microprices.index[0])
    log_returns_nmin.sort_index(inplace=True)

    #save
    output_name = os.path.join(output_path, str(nmin)+'min_' + str(date.date())+'.csv')
    log_returns_nmin.to_csv(output_name, header = False)

print('finished loop')

supplementary_path = os.path.join(os.path.pardir,TICKER +'_supplementary_files')
skipped_files_path = os.path.join(supplementary_path, str(nmin)+'min_skipped')
empty_files_path = os.path.join(supplementary_path, str(nmin)+'min_empty_time_intervals')
open_close_files_path = os.path.join(supplementary_path, str(nmin)+'min_opening_closing_times')

with open(skipped_files_path +'_orderbook.txt', 'wb') as fp:  
      pickle.dump(orderbook_with_problems, fp)

with open(skipped_files_path + '_messages.txt', 'wb') as fp:  
      pickle.dump(messages_with_problems, fp)
      
with open(empty_files_path + '.txt' , 'wb') as fp:  
      pickle.dump(empty_time_intervals, fp)
      
with open(open_close_files_path + '.txt' , 'wb') as fp:  
      pickle.dump(opening_closing_times, fp)
    
print('please check supplementary files before performing analysis')


