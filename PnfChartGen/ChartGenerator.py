# -*- coding: utf-8 -*-
"""
    **ChartGenerator.py**
    - Copyright (c) 2019, KNC Solutions Private Limited.
    - License: 'Apache License, Version 2.0'.
    - version: 1.0.0
"""
from PnfChartGen.DhelmPnfChartGenerator import DhelmPnfChartGenerator


class ChartGenerator:
    @staticmethod
    def gen_chart(df, symbol, exchange, box_type, calculation_method, reversal=3, box_size=-1, box_percentage=1,
                  folder='pnfchart'):
        DhelmPnfChartGenerator(df,
                               symbol,
                               exchange,
                               box_type,
                               calculation_method,
                               box_size,
                               reversal,
                               box_percentage,
                               folder)