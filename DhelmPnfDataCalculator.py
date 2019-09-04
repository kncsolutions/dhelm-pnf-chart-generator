# -*- coding: utf-8 -*-
"""
    **DhelmPnfDataCalculator.py**
    - Copyright (c) 2019, KNC Solutions Private Limited.
    - License: 'Apache License, Version 2.0'.
    - version: 1.0.0
"""
from Column import Column
from Parameters import Box
from Parameters import Types
import math


class DhelmPnfDataCalculator:
    """
    It calculates data points required to plot point and figure chart
    :param  df : The historical dataset. Must contain 'date', 'open', 'high', 'low', 'close' columns. The last row must be
    the latest data.
    :param  calculation_method : Point and figure chart data will be calculated either using closing values or using
    the high-low values. Valid values for this parameter are from {Types.Method_close, Types.Close}
    :param  box_type : The box sizes can be specified by some value or using some percentage of the latest item. This
    parameter specifies that which of the two options to be used.
    Valid values are from {Types.Method_value, Types.Method_percentage}
    :param box_size : Any custom box size. This will be valid only if box_type is Types.Method_value. If you want to use
    default box sizes use -1 as argument.
    :param reversal : The reversal amount. Default value is 3.
    :param box_percentage : In case the box_type is Types.Method_percentage, the percentage amount can be specified here.
    Default is 1 percent
    """
    def __init__(self, df, calculation_method=Types.Method_close, box_type=Types.Method_value, box_size=-1, reversal=3,
                 box_percentage=1):
        self.DEBUG = False
        self.all_columns = []
        self.column_data = []
        self.idx = 0
        self.box_type = box_type
        self.box_percentage = box_percentage
        self.calculation_method = calculation_method
        self.box_size = box_size
        self.reversal = reversal
        if self.reversal <= 0:
            self.reversal = 3
        self.df = df
        h = self.df['high'].tolist()
        l = self.df['low'].tolist()
        c = self.df['close'].tolist()
        time = self.df['date'].tolist()
        self.chart_gen_date = 'Not Available'
        self.close_latest = -1
        if len(time) > 0:
            self.chart_gen_date = time[len(time)-1]
            self.close_latest = c[len(c)-1]

        if self.calculation_method == Types.Method_close:
            self.calculate_pnf_data_close(c, time)
        elif self.calculation_method == Types.Method_highlow:
            self.calculate_pnf_data_highlow(c, h, l, time)

    def assign_box_size(self, val, c):
        if self.box_size == -1:
            if val < 0.25:
                self.box_size = 0.0625
            elif 0.25 <= val < 1.00:
                self.box_size = 0.125
            elif 1.00 <= val < 5.00:
                self.box_size = 0.25
            elif 5.00 <= val < 20.00:
                self.box_size = 0.50
            elif 20.00 <= val < 100.00:
                self.box_size = 1.00
            elif 100.00 <= val < 200.00:
                self.box_size = 2.00
            elif 200.00 <= val < 500.00:
                self.box_size = 4.00
            elif 500.00 <= val < 1000.00:
                self.box_size = 5.00
            elif 1000.00 <= val < 25000.00:
                self.box_size = 50.00
            else:
                self.box_size = 500.00

        if self.box_type == Types.Method_percentage:
            if self.box_percentage <= 0:
                self.box_percentage = 1
            self.box_size = math.ceil(((c[len(c) - 1] - 1) * float(self.box_percentage)) / 100)
            if self.box_size == 0:
                self.box_size = 1

    def calculate_pnf_data_close(self, c, time):
        val = c[len(c) - 1]
        rev = self.reversal
        self.assign_box_size(val, c)

        box = self.box_size
        to_reverse = False
        col = Column()
        for i in range(0, len(c)):
            if i == 0:
                col = self.init_column_close(c, time)
                to_reverse = False
            else:
                if col.type != Box.NA:
                    if col.type == Box.Xs:
                        if c[i] >= col.top:
                            col.top = float("{0:.2f}".format(col.top + math.floor((c[i] - col.top) / box) * box + box))
                        elif col.top > c[i] and col.top - c[i] >= rev * box:
                            self.idx = i
                            col.columnAdded = 1
                            tmp = col
                            self.all_columns.append(tmp)
                            self.column_data.append(
                                {"bottom": col.bottom, "top": col.top, "time": col.timestamp, "type": col.type})
                            to_reverse = True
                            if to_reverse:
                                col = self.init_column_close(c, time)
                            to_reverse = False
                    elif col.type == Box.Os:
                        if c[i] <= col.bottom:
                            col.bottom = float(
                                "{0:.2f}".format(col.bottom - math.floor((col.bottom - c[i]) / box) * box - box))
                        elif c[i] > col.bottom and c[i] - col.bottom >= rev * box:
                            self.idx = i
                            col.columnAdded = 1
                            tmp = col
                            self.all_columns.append(tmp)
                            self.column_data.append(
                                {"bottom": col.bottom, "top": col.top, "time": col.timestamp, "type": col.type})
                            to_reverse = True
                            if to_reverse:
                                col = self.init_column_close(c, time)
                            to_reverse = False

        if to_reverse:
            col = self.init_column_close(c, time)
        if col.type != Box.NA:
            if col.columnAdded == 0:
                col.columnAdded = 1
                tmp = col
                self.all_columns.append(tmp)
                self.column_data.append({"bottom": col.bottom, "top": col.top, "time": col.timestamp, "type": col.type})
        if self.DEBUG:
            for item in self.column_data:
                print("Type : " + item['type'] + " Top : " + str(item['top']) + " Bottom : " + str(item['bottom']))

    def init_column_close(self, data, time):
        c = Column()
        if len(self.all_columns) == 0:
            rand = data[self.idx]
            tm = time[self.idx]
            for i in range(len(data)):
                if data[i] - rand >= self.box_size:
                    c.bottom = float("{0:.2f}".format(rand))
                    c.top = float("{0:.2f}".format(
                        c.bottom + math.floor((data[i] - c.bottom) / self.box_size) * self.box_size + self.box_size))
                    c.type = Box.Xs
                    c.timestamp = tm
                    self.idx = i
                    break
                if rand - data[i] >= self.box_size:
                    c.top = rand
                    c.bottom = c.top - math.floor((c.top - data[i]) / self.box_size) * self.box_size - self.box_size
                    c.type = Box.Os
                    c.timestamp = tm
                    self.idx = i
                    break
        elif len(self.all_columns) > 0:
            tm = time[self.idx]
            if self.all_columns[len(self.all_columns) - 1].type == Box.Xs:
                c.top = float("{0:.2f}".format(self.all_columns[len(self.all_columns) - 1].top - self.box_size))
                c.bottom = float("{0:.2f}".format(
                    c.top - math.floor((c.top - data[self.idx]) / self.box_size) * self.box_size - self.box_size))
                if c.top - c.bottom < 3 * self.box_size:
                    c.bottom = c.top - 3 * self.box_size
                c.timestamp = tm
                c.type = Box.Os
                self.idx = self.idx + 1
            elif self.all_columns[len(self.all_columns) - 1].type == Box.Os:
                c.bottom = float("{0:.2f}".format(self.all_columns[len(self.all_columns) - 1].bottom + self.box_size))
                c.top = float("{0:.2f}".format(
                    c.bottom + math.floor((data[self.idx] - c.bottom) / self.box_size) * self.box_size+ self.box_size))
                c.timestamp = tm
                c.type = Box.Xs
                self.idx = self.idx + 1
        return c

    def calculate_pnf_data_highlow(self, c, h, l, time):
        val = c[len(c) - 1]
        rev = self.reversal
        self.assign_box_size(val, c)
        box = self.box_size
        to_reverse = False
        col = Column()
        for i in range(0, len(c)):
            if i == 0:
                col = self.init_column_highlow(h, l, time)
                to_reverse = False
            else:
                if col.type != Box.NA:
                    if col.type == Box.Xs:
                        if h[i] >= col.top:
                            col.top = float("{0:.2f}".format(col.top + math.floor((h[i] - col.top) / box) * box + box))
                        elif col.top > l[i] and col.top - l[i] >= rev * box:
                            self.idx = i
                            col.columnAdded = 1
                            tmp = col
                            self.all_columns.append(tmp)
                            self.column_data.append(
                                {"bottom": col.bottom, "top": col.top, "time": col.timestamp, "type": col.type})
                            to_reverse = True
                            if to_reverse:
                                col = self.init_column_highlow(h, l, time)
                            to_reverse = False
                    elif col.type == Box.Os:
                        if l[i] <= col.bottom:
                            col.bottom = float(
                                "{0:.2f}".format(col.bottom - math.floor((col.bottom - l[i]) / box) * box - box))
                        elif h[i] > col.bottom and h[i] - col.bottom >= rev * box:
                            self.idx = i
                            col.columnAdded = 1
                            tmp = col
                            self.all_columns.append(tmp)
                            self.column_data.append(
                                {"bottom": col.bottom, "top": col.top, "time": col.timestamp, "type": col.type})
                            to_reverse = True
                            if to_reverse:
                                col = self.init_column_highlow(h, l, time)
                            to_reverse = False
        if to_reverse:
            col = self.init_column_highlow(h, l, time)

        if col.type != Box.NA:
            if col.columnAdded == 0:
                col.columnAdded = 1
                tmp = c
                self.all_columns.append(tmp)
                self.column_data.append({"bottom": col.bottom, "top": col.top, "time": col.timestamp, "type": col.type})
        if self.DEBUG:
            for item in self.column_data:
                print("Type : " + item['type'] + " Top : " + str(item['top']) + " Bottom : " + str(item['bottom']))

    def init_column_highlow(self, h, l, time):
        c = Column()
        if len(self.all_columns) == 0:
            rand1 = h[self.idx]
            rand2 = l[self.idx]
            tm = time[self.idx]
            for i in range(len(h)):
                if h[i] - rand1 >= self.box_size:
                    c.bottom = float("{0:.2f}".format(rand1))
                    c.top = float("{0:.2f}".format(
                        c.bottom + math.floor((h[i] - c.bottom) / self.box_size) * self.box_size + self.box_size))
                    c.type = Box.Xs
                    c.timestamp = tm
                    self.idx = i
                    break
                if rand2 - l[i] >= self.box_size:
                    c.top = rand2
                    c.bottom = c.top - math.floor((c.top - l[i]) / self.box_size) * self.box_size - self.box_size
                    c.type = Box.Os
                    c.timestamp = tm
                    self.idx = i
                    break
        elif len(self.all_columns) > 0:
            tm = time[self.idx]
            if self.all_columns[len(self.all_columns) - 1].type == Box.Xs:
                c.top = float("{0:.2f}".format(self.all_columns[len(self.all_columns) - 1].top - self.box_size))
                c.bottom = float("{0:.2f}".format(
                    c.top - math.floor((c.top - l[self.idx]) / self.box_size) * self.box_size - self.box_size))
                if c.top - c.bottom < 3 * self.box_size:
                    c.bottom = c.bottom - 3 * self.box_size
                c.timestamp = tm
                c.type = Box.Os
                self.idx = self.idx + 1
            elif self.all_columns[len(self.all_columns) - 1].type == Box.Os:
                c.bottom = float("{0:.2f}".format(self.all_columns[len(self.all_columns) - 1].bottom + self.box_size))
                c.top = float("{0:.2f}".format(
                    c.bottom + math.floor((h[self.idx] - c.bottom) / self.box_size) * self.box_size + self.box_size))
                if c.top - c.bottom < 3 * self.box_size:
                    c.top = c.top + 3 * self.box_size
                c.timestamp = tm
                c.type = Box.Xs
                self.idx = self.idx + 1
        return c
    """
    :return Returns the box size.
    """
    def get_box_size(self):
        return self.box_size

    """
    :return Returns data for point and figure chart column wise.
    """

    def get_columns(self):
        return self.column_data

    """
    :return Returns the date-time on which the data has been calculated.
    """

    def get_chart_date(self):
        return self.chart_gen_date

    """
    :return Returns the latest closing value.
    """

    def get_close_latest(self):
        return self.close_latest
