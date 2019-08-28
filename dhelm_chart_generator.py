import datetime
import pandas as pd
import time
import Parameters
from Gen_Pnf_WIth_Quandl_Data import Gen_Pnf_With_Quandl_Data
from Gen_Pnf_With_Gfeed_Data import  Gen_Pnf_With_Gfeed_Data
from Gen_Pnf_With_Zerodha_Kite_Data import Gen_Pnf_With_Zerodha_Kite_Data

settings = pd.read_excel('settings/data_source_credentials.xlsx')
data_source = settings.at[settings.first_valid_index(), 'data_source']
if Parameters.DataSource.GLOBAL_DATA_FEED in data_source or data_source == 1:
    data = Gen_Pnf_With_Gfeed_Data()
elif Parameters.DataSource.QUANDL in data_source or data_source == 2:
    data = Gen_Pnf_With_Quandl_Data()
elif Parameters.DataSource.ZERODHA in data_source or data_source == 3:
    data = Gen_Pnf_With_Zerodha_Kite_Data()