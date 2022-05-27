import os
import glob
import pandas as pd

nmin = 1
TICKER ='SPY'

data_path = os.path.join('data', TICKER, TICKER +'_equidistant_log_returns')
os.chdir(data_path)

extension = 'csv'
csv_file_list = [i for i in glob.glob('*.{}'.format(extension))]

CHUNK_SIZE = 100000

output_file = os.path.join(os.path.pardir,TICKER + '_' + str(nmin) + 'min_preprocessed_data.csv')

for csv_file_name in csv_file_list:
    chunk_container = pd.read_csv(csv_file_name, chunksize = CHUNK_SIZE)
    for chunk in chunk_container:
        chunk.to_csv(output_file, mode="a", index=False)
        

