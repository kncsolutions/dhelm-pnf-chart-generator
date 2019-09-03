# -*- coding: utf-8 -*-
"""
    **CredentialLoader.py**
    - Copyright (c) 2019, KNC Solutions Private Limited.
    - License: 'Apache License, Version 2.0'.
    - version: 1.0.0
"""
import pandas as pd

"""
Class to handle the credentials related to quandl
"""


class Quandl_API_KEY:
    @staticmethod
    def get_quandl_api_key():
        data = pd.read_csv('settings/quandl_credentials.csv')
        if data.at[data.first_valid_index(), 'api_key'] is None:
            raise Exception('Api key is empty or invalid.')
        return data.at[data.first_valid_index(), 'api_key']

"""
Class to handle the credentials related to Global Data Feed
"""


class Gfeed_URI_API_KEY:
    @staticmethod
    def get_gfeed_uri_api_key():
        data = pd.read_csv('settings/gfeed_credentials.csv')
        if data.at[data.first_valid_index(), 'gfeed_ws_endpoint'] is None:
            raise Exception('Api key is empty or invalid.')
        if data.at[data.first_valid_index(), 'gfeed_api_key'] is None:
            raise Exception('Api key is empty or invalid.')
        return [data.at[data.first_valid_index(), 'gfeed_ws_endpoint'], data.at[data.first_valid_index(), 'gfeed_api_key']]
"""
Class to handle the credentials related to Zerodha kite api
"""


class KITE_API_KEY_ACCESS_TOKEN:
    @staticmethod
    def get_kite_credentials():
        data = pd.read_csv('settings/kite_credentials.csv')
        if data.at[data.first_valid_index(), 'api_key'] is None:
            raise Exception('Api key is empty or invalid.')
        if data.at[data.first_valid_index(), 'access_token'] is None:
            raise Exception('Api key is empty or invalid.')
        return [data.at[data.first_valid_index(), 'api_key'], data.at[data.first_valid_index(), 'access_token']]
