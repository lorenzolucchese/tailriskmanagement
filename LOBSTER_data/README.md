# LOBSTER-data-processing

Pre-processing code for data downloaded from LOBSTER (https://lobsterdata.com/). 

## Overview
_data_to_equidistant_timeseries.py_ and _merge_csv.py_ merge the data from from the orderbook and message files (for a specific ticker) is in order to create a high frequency equispaced time series of intra-day log returns (open-to-close). _data_to_daily_timeseries.py_ produces the corresponding close-to-close log-returns time series. Note that overnight returns are implicitly included in the _TICKER_daily_log_returns_ output file (close-to-close returns) but excluded in the _TICKER_equidistant_log_returns_ output file (open-to-close returns only).

## Input: 	

A _TICKER_ folder with _TICKER_equidistant_log_returns_ and _TICKER_supplementary_files_ sub-folders need to be created and set as working directory.
The data downloaded from LOBSTER needs to be stored in a folder named _TICKER_extracted_data_ in the _TICKER_ folder and possibly subdivided by month.
In each folder a trading day is represented by two _.csv_ files, the message and orderbook files as downloaded from LOBSTER.
The variable _nmin_, the time delta at which high frequency data is required, needs to be selected (for example 1-min spaced data) as well as the _TICKER_ variable.

## Code:

_data_to_equidistant_timeseries.py_ reads all _.csv_ files in the _TICKER_extracted_data_ folder and loops through them:

1. For each trading day the orderbook file is read as a dataframe (with columns _ASKp1_, _ASKs1_, _BIDp1_, _BIDs1_) and the corresponding times are read off the message file (in datetime form).

2. The orderbook is reduced to only the rows corresponding to the equispaced time points (more specifically the last orderbook row before each time point is selected, except for the opening price). 

3. The prices at the equispaced time points are computed using a weighted average of the BID-ASK prices and the correct time-indexing is assigned.

4. The log-returns are then computed by logarithmic differencing and stored in the _TICKER_equidistant_log_returns_ folder as _.csv_ files named _nmin_date.csv_.

_merge_csv.py_ then merges all the _.csv_ files in the _TICKER_equidistant_log_returns_ into one named _TICKER_preprocessed_data.csv_. (note that _.csv_ files can be removed/added before merging).

_data_to_daily_timeseries.py_ reads all orderbook _.csv_ files in the _TICKER_extracted_data_ folder and loops through them, for each computing the closing price by a weighted average of the last BID-ASK prices of the day. The close-to-close log-returns are then computed through logarithmic differencing and saved in the file _TICKER_daily_log_returns.csv_.

## Output: 

The open-to-close high frequency equispaced data is hence returned in both the _TICKER_equidistant_log_returns_ folder as one _.csv_ file per day and in a single merged file named _TICKER_preprocessed_data.csv_. The daily close-to-close returns are saved in a file named _TICKER_daily_log_returns.csv_.

Supplementary files produced, to check before using the data, are:
	
_nmin_skipped_messages_: message files which pandas didn't manage read
	
_nmin_skipped_orderbook_: orderbook files which pandas didn't manage read

_nmin_empty_time_intervals_: trading days where data is scarse (i.e. there are time-intervals without transactions and the price is henced assumed to not change).

_nmin_opening_closing_times_: trading days with "strange" opening and closing times (i.e. which are not 9:30-16:00)
