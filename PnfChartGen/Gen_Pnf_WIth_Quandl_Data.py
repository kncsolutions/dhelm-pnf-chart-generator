# -*- coding: utf-8 -*-
"""
    **Gen_Pnf_With_Quandl_Data.py**
    - Copyright (c) 2019, KNC Solutions Private Limited.
    - License: 'Apache License, Version 2.0'.
    - version: 1.0.0
"""

import quandl
import pandas as pd
import datetime
from PnfChartGen.Parameters import *
from PnfChartGen.CredentialLoader import Quandl_API_KEY
from PnfChartGen.ChartGenerator import ChartGenerator


class Gen_Pnf_With_Quandl_Data:
    """
    This class generates point and figure chart after extracting data from quandl.
    """
    def __init__(self):
        quandl.ApiConfig.api_key = Quandl_API_KEY.get_quandl_api_key()
        self.__config = (pd.read_excel('settings/dhelm_pnf_chart_gen_settings.xlsx'))
        from_date = (self.__config.at[self.__config.first_valid_index(), 'from_dt']).strftime("%Y-%m-%d")
        to_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.__list_stocks = pd.read_csv('settings/quandl_chart_gen_list.csv')
        for index, row in self.__list_stocks.iterrows():
            self.__exchange = row['exchange']
            self.__data_historical = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            self.__tmp = quandl.get(self.__exchange+'/' + row['tradingsymbol'], start_date=from_date, end_date=to_date)
            self.__tmp['Date'] = self.__tmp.index
            self.__tmp.index = range(len(self.__tmp))
            if 'Close' not in self.__tmp.columns:
                raise Exception('Invalid data.')
            self.__data_historical['date'] = self.__tmp.Date
            self.__data_historical['open'] = self.__tmp['Open']
            self.__data_historical['high'] = self.__tmp['High']
            self.__data_historical['low'] = self.__tmp['Low']
            self.__data_historical['close'] = self.__tmp['Close']
            self.__data_historical['volume'] = self.__tmp['No. of Shares']
            if self.__config.at[self.__config.first_valid_index(), 'method_percentage']:
                self.__box_type = Types.Method_percentage
            else:
                self.__box_type = Types.Method_value
            if 'close' in self.__config.at[self.__config.first_valid_index(), 'calculation_method']:
                self.__calculation_method = Types.Method_close
            else:
                self.__calculation_method = Parameters.Types.Method_highlow
            self.__box_size = (self.__config.at[self.__config.first_valid_index(), 'BOX_SIZE'])
            self.__reversal = (self.__config.at[self.__config.first_valid_index(), 'REVERSAL'])
            self.__box_percentage = (self.__config.at[self.__config.first_valid_index(), 'BOX_PERCENTAGE'])
            self.__folder = 'charts_quandl'
            print('Generating point and figure chart for '+ row['tradingsymbol'])
            ChartGenerator.gen_chart(self.__data_historical,
                                     row['tradingsymbol'],
                                     self.__exchange,
                                     self.__box_type,
                                     self.__calculation_method,
                                     self.__reversal,
                                     self.__box_size,
                                     self.__box_percentage,
                                     self.__folder)
            print('DONE..Check for chart in the folder '+self.__folder+'.')
