from DhelmPnfChartGenerator import DhelmPnfChartGenerator
"""

"""


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