import quandl
import pandas as pd
import datetime
from collections import OrderedDict, Counter
from kiteconnect import KiteConnect
from kiteconnect import exceptions
import requests
import Parameters
import CredentialLoader
from ChartGenerator import ChartGenerator
"""

"""


class Gen_Pnf_With_Zerodha_Kite_Data:
    def __init__(self):
        self.__credentials = CredentialLoader.KITE_API_KEY_ACCESS_TOKEN.get_kite_credentials()
        self.__config = (pd.read_excel('settings/dhelm_pnf_chart_gen_settings.xlsx'))
        self.__client = KiteConnect(self.__credentials[0])
        self.__client.set_access_token(self.__credentials[1])
        self.__from_date = (self.__config.at[self.__config.first_valid_index(), 'from_dt']).strftime("%Y-%m-%d %H:%M:%S")
        self.__to_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__list_stocks = pd.read_csv('settings/kite_chart_gen_list.csv')
        if self.__config.at[self.__config.first_valid_index(), 'method_percentage']:
            self.__box_type = Parameters.Types.Method_percentage
        else:
            self.__box_type = Parameters.Types.Method_value
        if 'close' in self.__config.at[self.__config.first_valid_index(), 'calculation_method']:
            self.__calculation_method = Parameters.Types.Method_close
        else:
            self.__calculation_method = Parameters.Types.Method_highlow
        self.__box_size = (self.__config.at[self.__config.first_valid_index(), 'BOX_SIZE'])
        self.__reversal = (self.__config.at[self.__config.first_valid_index(), 'REVERSAL'])
        self.__box_percentage = (self.__config.at[self.__config.first_valid_index(), 'BOX_PERCENTAGE'])
        self.__folder = 'charts_kite'
        for index, row in self.__list_stocks.iterrows():
            self.__data_historical = self.__get_historical_data(row)
            print(self.__data_historical)
            print('Generating point and figure chart for ' + row['tradingsymbol'])
            ChartGenerator.gen_chart(self.__data_historical,
                                     row['tradingsymbol'],
                                     row['exchange'],
                                     self.__box_type,
                                     self.__calculation_method,
                                     self.__reversal,
                                     self.__box_size,
                                     self.__box_percentage,
                                     self.__folder)
            print('DONE..Check for chart in the folder ' + self.__folder + '.')

    def __get_historical_data(self, row):
        hist = None
        df = pd.DataFrame()
        try:
            hist = self.__client.historical_data(int(row['instrument_token']), self.__from_date, self.__to_date, 'day', False)
        except requests.exceptions.ReadTimeout:
            pass
        except exceptions.NetworkException:
            pass
        except Exception:
            pass
        if hist is not None:
            for entry in hist:
                if 'date' in entry:
                    entry['date'] = str(entry['date'])
            col = Counter()
            for k in list(hist):
                col.update(k)
                df = pd.DataFrame([k.values() for k in hist], columns=col.keys())
        return df
