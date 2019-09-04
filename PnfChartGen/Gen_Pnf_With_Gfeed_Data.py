# -*- coding: utf-8 -*-
"""
    **Gen_Pnf_With_Gfeed_Data.py**
    - Copyright (c) 2019, KNC Solutions Private Limited.
    - License: 'Apache License, Version 2.0'.
    - version: 1.0.0
"""
import pandas as pd
import datetime
import json
import time
import pytz
import tzlocal
from collections import OrderedDict, Counter
from DhelmGfeedClient.gfeedclient import GfeedClient
from DhelmGfeedClient.constants import Constants
from PnfChartGen.Parameters import *
from PnfChartGen.CredentialLoader import Gfeed_URI_API_KEY
from PnfChartGen.ChartGenerator import ChartGenerator


class Gen_Pnf_With_Gfeed_Data:
    """
    This class generates point and figure chart after extracting historical data from Global Datafeed websocket api.
    """
    def __init__(self):
        self.debug = False
        self.__credentials = Gfeed_URI_API_KEY.get_gfeed_uri_api_key()
        self.__config = (pd.read_excel('settings/dhelm_pnf_chart_gen_settings.xlsx'))
        self.__client = GfeedClient(self.__credentials[0], self.__credentials[1])
        self.__list_stocks = pd.read_csv('settings/gfeed_chart_gen_list.csv')
        self.__df_list_historical_names = []
        self.__df_list_historical = []
        if self.__config.at[self.__config.first_valid_index(), 'method_percentage']:
            self.__box_type = Types.Method_percentage
        else:
            self.__box_type = Types.Method_value
        if 'close' in self.__config.at[self.__config.first_valid_index(), 'calculation_method']:
            self.__calculation_method = Types.Method_close
        else:
            self.__calculation_method = Types.Method_highlow
        self.__box_size = (self.__config.at[self.__config.first_valid_index(), 'BOX_SIZE'])
        self.__reversal = (self.__config.at[self.__config.first_valid_index(), 'REVERSAL'])
        self.__box_percentage = (self.__config.at[self.__config.first_valid_index(), 'BOX_PERCENTAGE'])
        self.__folder = 'charts_gfeed'
        for index, row in self.__list_stocks.iterrows():
            self.__list_stocks.loc[index, 'is_data_extracted'] = False
            self.__list_stocks.loc[index, 'is_chart_generated'] = False

        def on_authenticated(base_client):
            from_date = (self.__config.at[self.__config.first_valid_index(), 'from_dt'])
            to_date = datetime.datetime.now()
            to_date = pytz.timezone('Asia/Calcutta').localize(to_date)
            for index, row in self.__list_stocks.iterrows():
                if not row['is_data_extracted']:
                    self.__exchange = row['exchange'].upper()
                    self.__tradingsymbol = row['tradingsymbol'].upper()
                    base_client.get_historical_ohlc_data(self.__exchange, self.__tradingsymbol, Constants.DAY,
                                                        int(time.mktime(from_date.timetuple())),
                                                        int(time.mktime(to_date.timetuple())))

        def on_message_historical_ohlc_data(base_client, historical_ohlc_data):
            if self.debug:
                print("\n*********HISTORICAL OHLC DATA*************\n")
                print(historical_ohlc_data)
            request = historical_ohlc_data['Request']
            if self.debug:
                print(request)
            for i, r in self.__list_stocks.iterrows():
                if r['tradingsymbol'].upper() == request['InstrumentIdentifier']:
                    self.__list_stocks.loc[i, 'is_data_extracted'] = True
                    break
            self.__data_historical = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            col = Counter()
            for k in list(historical_ohlc_data['Result']):
                col.update(k)
                tmp = pd.DataFrame([k.values() for k in historical_ohlc_data['Result']], columns=col.keys())
            self.__data_historical['date'] = tmp['LastTradeTime']
            self.__data_historical['open'] = tmp['Open']
            self.__data_historical['high'] = tmp['High']
            self.__data_historical['low'] = tmp['Low']
            self.__data_historical['close'] = tmp['Close']
            self.__data_historical['volume'] = tmp['TradedQty']
            for i, r in self.__data_historical.iterrows():
                self.__data_historical.loc[i, 'date'] = datetime.datetime.fromtimestamp(r['date'], datetime.timezone.utc)\
                    .astimezone(pytz.timezone("Asia/Calcutta")).strftime('%Y-%m-%d %H:%M:%S')
            self.__data_historical = self.__data_historical.iloc[::-1].reset_index(drop=True)
            self.__df_list_historical.append(self.__data_historical)
            self.__df_list_historical_names.append(request['InstrumentIdentifier'])
            last_date_in_list = self.__data_historical.at[self.__data_historical.last_valid_index(), 'date']
            last_date_in_list = datetime.datetime.strptime(str(last_date_in_list), '%Y-%m-%d %H:%M:%S').date()
            current_date = datetime.date.today()
            if current_date > last_date_in_list:
                base_client.get_last_quote(request['Exchange'], request['InstrumentIdentifier'])
            else:
                for index, row in self.__list_stocks.iterrows():
                    if row['tradingsymbol'] == request['InstrumentIdentifier']:
                        if not row['is_chart_generated']:
                            self.__gen_chart(self.__data_historical,
                                             request['InstrumentIdentifier'],
                                             request['Exchange'])
                            self.__list_stocks[index, 'is_chart_generated'] = True

        def on_message_last_quote(base_client, last_quote):
            if self.debug:
                print("\n*********LAST QUOTE*************\n")
                print(last_quote)
            index = self.__data_historical.last_valid_index() + 1
            quote_date = datetime.datetime.fromtimestamp(last_quote['LastTradeTime'], datetime.timezone.utc) \
                         .astimezone(pytz.timezone("Asia/Calcutta")).strftime('%Y-%m-%d %H:%M:%S')
            quote_date_formatted = datetime.datetime.strptime(str(quote_date), '%Y-%m-%d %H:%M:%S').date()

            for i in range(len(self.__df_list_historical_names)):
                if self.__df_list_historical_names[i] == last_quote['InstrumentIdentifier']:
                    list_last_date = self.__df_list_historical[i].at[self.__df_list_historical[i].last_valid_index(), 'date']
                    list_last_date_formatted = datetime.datetime.strptime(str(list_last_date),
                                                                          '%Y-%m-%d %H:%M:%S').date()
                    if quote_date_formatted > list_last_date_formatted:
                        self.__df_list_historical[i].loc[index, 'date'] = quote_date
                        self.__df_list_historical[i].loc[index, 'open'] = last_quote['Open']
                        self.__df_list_historical[i].loc[index, 'high'] = last_quote['High']
                        self.__df_list_historical[i].loc[index, 'low'] = last_quote['Low']
                        self.__df_list_historical[i].loc[index, 'close'] = last_quote['Close']
                        self.__df_list_historical[i].loc[index, 'volume'] = last_quote['TotalQtyTraded']
                        if self.debug:
                            print(self.__df_list_historical[i])
                    for index, row in self.__list_stocks.iterrows():
                        if row['tradingsymbol'] == last_quote['InstrumentIdentifier']:
                            if not row['is_chart_generated']:
                                self.__gen_chart(self.__df_list_historical[i],
                                                 last_quote['InstrumentIdentifier'],
                                                 last_quote['Exchange'])
                                self.__list_stocks[index, 'is_chart_generated'] = True
                    break

        self.__client.on_authenticated = on_authenticated
        self.__client.on_message_historical_ohlc_data = on_message_historical_ohlc_data
        self.__client.on_message_last_quote = on_message_last_quote
        self.__client.connect()

    def __gen_chart(self, df, symbol, exchange):
        print('Generating point and figure chart for ' + symbol)
        ChartGenerator.gen_chart(df,
                                 symbol,
                                 exchange,
                                 self.__box_type,
                                 self.__calculation_method,
                                 self.__reversal,
                                 self.__box_size,
                                 self.__box_percentage,
                                 self.__folder)
        print('DONE..Check for chart in the folder ' + self.__folder + '.')
