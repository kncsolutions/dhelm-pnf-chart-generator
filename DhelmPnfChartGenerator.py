# -*- coding: utf-8 -*-
"""
    **DhelmPnfChartGenerator.py**
    - Copyright (c) 2019, KNC Solutions Private Limited.
    - License: 'Apache License, Version 2.0'.
    - version: 1.0.0
"""
import xlsxwriter
from DhelmPnfDataCalculator import DhelmPnfDataCalculator
from Parameters import Box
from Parameters import Types
import time


class DhelmPnfChartGenerator:
	"""
	It plots point and figure chart in excel and saves the chart in the specified location.
	:param  df : The historical dataset. Must contain 'date', 'open', 'high', 'low', 'close' columns. The last row must be
	the latest data.
	:param scrip : The trading symbol/scrip identifier
	:param exchange : The related exchange.
	:param  box_type : The box sizes can be specified by some value or using some percentage of the latest item. This
	parameter specifies that which of the two options to be used.
	Valid values are from {Types.Method_value, Types.Method_percentage}
	:param  calculation_method : Point and figure chart data will be calculated either using closing values or using
	the high-low values. Valid values for this parameter are from {Types.Method_close, Types.Close}
	:param box_size : Any custom box size. This will be valid only if box_type is Types.Method_value. If you want to use
	default box sizes use -1 as argument.
	:param reversal : The reversal amount. Default value is 3.
	:param box_percentage : In case the box_type is Types.Method_percentage, the percentage amount can be specified here.
	Default is 1 percent
	:param folder : The relative path of the folder. Default value is 'pnfchart'. By default charts are stored in 'pnfchart'
	folder.
	"""
	def __init__(self, df, scrip, exchange, box_type=Types.Method_value, calculation_method=Types.Method_close, box_size=-1,
				reversal=3, box_percentage=1, folder='pnfchart'):
		self.df = df
		self.all_columns = []
		self.column_data = []
		self.idx = 0
		self.box_size = box_size
		self.reversal = reversal
		self.scrip = scrip
		self.exchange = exchange
		self.offsetY = 3
		self.row_START = 10
		self.row_END = 10
		self.box_type = box_type
		self.box_percentage = box_percentage
		self.folder = folder
		self.calculation_method = calculation_method
		self.pnf_chart_generated = False
		self.candle_chart_generated = False
		self.chart_gen_date = 'Not Available'
		self.close_latest = -1
		self.__prepare_chart()

	def __prepare_chart(self):
			self.chart_gen_date = 'Not Available'
			if not self.pnf_chart_generated:
				pnf = DhelmPnfDataCalculator(self.df,
											 self.calculation_method,
											 self.box_type,
											 self.box_size,
											 self.reversal,
											 self.box_percentage)
				self.chart_gen_date = pnf.get_chart_date()
				self.close_latest = pnf.get_close_latest()
				self.box_size = pnf.get_box_size()
				self.column_data = pnf.get_columns()
				if len(self.column_data) > 3:
					self.__plot_pnf_data()
	
	def __plot_pnf_data(self):
		min_val = self.__get_min_value()-self.box_size*self.offsetY
		max_val = self.__get_max_value()+self.box_size*self.offsetY
		num_rows = int((max_val-min_val)/self.box_size)
		num_cols = len(self.column_data)
		Ys = []
		Y = []
		yVals = []
		y = min_val
		for i in range(num_rows):
			Y.append(i+self.row_START)
			Ys.append(i+self.row_START)
			yVals.append(float("{0:.2f}".format(y)))      
			y = y+self.box_size
		Y.reverse()
		self.row_END = self.row_START+num_rows-1
		txt1 = 'Exchange : ' + self.exchange+' ||  Scrip : '+self.scrip
		txt2 = 'Type : '+self.calculation_method+' || Date : '+str(self.chart_gen_date)
		txt3 = 'Box : '+str(self.box_size)+' || Close : '+str(self.close_latest)
		txt4 = 'Reversal : '+str(self.reversal)
		workbook = xlsxwriter.Workbook(self.folder+'/'+self.scrip+'_'+self.calculation_method+'.xlsx')
		# The workbook object is then used to add new  
		# worksheet via the add_worksheet() method. 
		worksheet = workbook.add_worksheet('PnF')
		worksheet.set_default_row(12)
		worksheet.set_column(1,num_cols+10,1.44)
		merge_format = workbook.add_format({
		'bold': 1,
		'border': 1,
		'align': 'center',
		'valign': 'vcenter'})
		cell_format = workbook.add_format({
		'border': 1,
		'align': 'center',
		'valign': 'vcenter',
		'font_size':8,
		'bold':1
		})
		cell_format_date = workbook.add_format({
		'border': 1,
		'align': 'center',
		'valign': 'vcenter',
		'font_size':8,
		'bold':1,
		'rotation':90
		})
		cell_format_X = workbook.add_format({
		'border': 1,
		'align': 'center',
		'valign': 'vcenter',
		'font_color':'blue',
		'font_size':11
		})
		cell_format_O = workbook.add_format({
		'border': 1,
		'align': 'center',
		'valign': 'vcenter',
		'font_color':'red',
		'font_size':11
		})
		cell_format_close = workbook.add_format({
			'border': 1,
			'align': 'center',
			'valign': 'vcenter',
			'bg_color': 'a4adcc',
			'font_size': 11
		})
		for i in range(num_rows+10):
			for j in range(num_cols+10):
				worksheet.write(i, j, '', cell_format)
		for j in range(1, num_cols+10):
				worksheet.write(num_rows+11, j, '', cell_format_date)

		worksheet.merge_range("A1:Z2", txt1, merge_format)
		worksheet.merge_range("A3:Z4", txt2, merge_format)
		worksheet.merge_range("A5:Z6", txt3, merge_format)
		worksheet.merge_range("A7:Z8", txt4, merge_format)
		worksheet.set_row(num_rows+11, 100)  # Set the height of Row 1 to 20.
		row = Ys[0]
		
		col = 0
		for i in reversed(yVals):
			worksheet.write(row, col, str(i),cell_format)
			row = row+1
		coll = 1
		for item in self.column_data:
			row_low = -1
			row_high = -1
			num_boxes = int(round((item['top']-item['bottom'])/self.box_size))
			if item['type'] == Box.Xs:
				for i in range(len(yVals)-1):
					if yVals[i] <= item['bottom'] < yVals[i + 1]:
						row_low = Y[i-1]
						break
				row_high = row_low-num_boxes
				for j in range(row_high, row_low):
					worksheet.write(j, coll, 'X', cell_format_X)
			if item['type'] == Box.Os:
				for i in range(1, len(yVals)-1):
					if yVals[i] >= item['top'] > yVals[i - 1]:
						row_high = Y[i-1]
				row_low = row_high+num_boxes
				for j in range(row_high, row_low):
					worksheet.write(j, coll, 'O', cell_format_O)
			if not isinstance(item['time'], str):
				time_stamp = item['time'].strftime("%Y-%m-%d %H:%M:%S")
			else:
				time_stamp = item['time']
			worksheet.write(num_rows+11, coll, time_stamp, cell_format_date)
			coll = coll+1
		workbook.close()
		self.pnf_chart_generated = True

	def __get_min_value(self):
		min_val = self.column_data[0]['bottom']
		for col in self.column_data:
			if col['bottom'] < min_val:
				min_val = col['bottom']
		return min_val

	def __get_max_value(self):
		max_val=self.column_data[0]['bottom']
		for col in self.column_data:
			if col['top'] > max_val:
				max_val = col['top']
		return max_val