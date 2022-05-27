# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 16:52:54 2021

@author: Lorenzo
"""

import os
import glob
import pandas as pd
import re
import datetime
import numpy as np

TICKER = 'SPY'

os.chdir(os.path.join('data', TICKER, TICKER+'_extracted_files'))

extension = 'csv'
dir_paths = os.listdir()
csv_file_list = []

#get a list of all subdirectories and search for csv files in these subdirectories

for dir_path in dir_paths:
    file_path = os.path.join(dir_path,'*.{}'.format(extension))
    csv_file_list_to_add = [i for i in glob.glob(file_path)]
    csv_file_list += csv_file_list_to_add

csv_orderbook = [name for name in csv_file_list if 'orderbook' in name]
df_closing_prices = pd.DataFrame()

for orderbook_name in csv_orderbook:

    #read the orderbook. keep a record of problematic files
    try:
        df_orderbook = pd.read_csv(orderbook_name, header= None)
    except:
        print('the following file has been skipped:  ' + orderbook_name)
        continue

    df_orderbook.columns = ("ASKp1" , "ASKs1" , "BIDp1",  "BIDs1")

    #get date first
    match = re.findall('\d{4}-\d{2}-\d{2}', orderbook_name)[-1]
    date = datetime.datetime.strptime(match, '%Y-%m-%d')
    
    # compute the closing price
    closing_price = (df_orderbook['ASKp1'].iloc[-1] * df_orderbook['ASKs1'].iloc[-1] + df_orderbook['BIDp1'].iloc[-1] * df_orderbook['BIDs1'].iloc[-1]) / (df_orderbook['ASKs1'].iloc[-1] + df_orderbook['BIDs1'].iloc[-1])
    df_closing_price = pd.DataFrame(data = [closing_price], index = pd.Series(date))
    df_closing_prices = df_closing_prices.append(df_closing_price)
    
#compute daily log returns
log_returns = (np.log(df_closing_prices)).diff(1).drop(df_closing_prices.index[0])
log_returns.sort_index(inplace=True)

#save
output_name = os.path.join(os.path.pardir, TICKER +'_daily_log_returns' + '.csv')
log_returns.to_csv(output_name, header = False)

