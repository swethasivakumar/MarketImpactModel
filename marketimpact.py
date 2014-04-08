import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import csv
import QSTK.qstkstudy.EventProfiler as ep
import csv
import glob
import os
import re
import collections

ofile = "day2.csv"
#market_file = "market.csv"
market_file = "market_new.csv"

market_capital = {}
norm_market_capital = {}
stocks = {}
minute_vol = {}

'''This method gets the list of all the CSV files in the directory. Hidden files are omitted. It returns a list of all the file names'''
def getFileNames():
	files = []
	count = 0
	for file in os.listdir("."):
		if not file.startswith('.'):
    			if file.endswith(".csv"):
        			files.append(file)
				count += 1
	print count
	return files


'''This method reads every file (every stock) and retrives the data for the last day. It considers the time period from 10am to 3pm. It also parses the filename and gets the symbol of the stock and appends it as a new column'''
def getdata(files):
	symbols = []
	transactions = []
	writer = csv.writer(open (ofile, 'wb'))
	for f in files:
		with open (f, 'rb') as fh:
			reader = csv.reader(fh)
			filename = re.split(r'[_.]+',f)
			symbol = filename[1]
			print symbol
			for line in reader:
				if line[0] == '20140314' and int(line[1])>=1000 and int(line[1])<=1500:
					line.append(symbol)
					transactions.append(line)	
					writer.writerow(line)

	return transactions		



'''Don't use this as of now as the file is being written in the previous method'''
def writeToFile(transactions):
	writer = csv.writer(open (ofile, 'wb'))
	for line in transactions:
		writer.writerow(line)

		
'''This method reads the file output in 'getdata' and adds up the total volume of all the stocks traded in a particular minute. It maintains a dictionary with time(minute) as the key and the total volume of all stocks in that minute as the value'''
def dollarVolumeMinute (ofile):
	minute_vol_temp = {}
	reader = csv.reader( open (ofile, 'rb'))
	for row in reader:
		minute = row[1]
		if minute in minute_vol_temp.keys():
			minute_vol_temp[minute] += float(row[5])*float(row[6])
		else:
			minute_vol_temp[minute] = float(row[5])*float(row[6])	
	#minute_vol = minute_vol_temp
	minute_vol = collections.OrderedDict(sorted(minute_vol_temp.items()))
	return minute_vol



'''This methods creates a market file which shows the general trend in the market. It calculates the market capitalization from the output file from 'getdata' for each minute. It normalizes using the sum of all market capitalization values'''
def createMarketFile(ofile):
	market_capital = {}
	norm_mc = {}
	reader = csv.reader( open (ofile, 'rb'))
	for row in reader:
		minute = row[1]
		if minute in market_capital.keys():
			market_capital[minute] += float(row[5])*float(row[6])
		else:
			market_capital[minute] = float(row[5])*float(row[6])

	#volume = volumeMinute(ofile)
	
	#taking the sum of market capital values instead of sum of volumes
	volume=0
	for minute in market_capital.keys():
		volume += market_capital[minute]

	for minute in market_capital.keys():
		#market_capital[minute] /= volume[minute]
		market_capital[minute] /= volume

	sorted_market_capital = collections.OrderedDict(sorted(market_capital.items()))
	
	for minute in sorted_market_capital.keys():
		norm_mc[minute] = sorted_market_capital[minute]/sorted_market_capital['1000']
	sorted_norm_mc = collections.OrderedDict(sorted(norm_mc.items()))
#	print sorted_norm_mc
	return sorted_market_capital, sorted_norm_mc



'''This method creates 2 files- normalized market files.. should check which one is right'''
def writeMarketFile(marketCapital):
	writer = csv.writer(open (market_file, 'wb'))
        for key, value  in marketCapital.items():
                writer.writerow([key, value])
	



'''This method calculates the market capital for each stock for every minute. It gets the dollar volume of every stock in a minute and normalizes using the total dollar volume of that minute. '''
def stockMarketCapitalMinute():
	minute_vol = {}
	reader = csv.reader( open (ofile, 'rb'))
	minute_vol = dollarVolumeMinute(ofile)
        for row in reader:
                stock = row[10]
		minute = row[1]
		dollarVol = float(row[5])*float(row[6])
		normDollarVol = float(dollarVol/minute_vol[minute])
                if stock in stocks.keys():
			tempMinutes = stocks[stock]
                        if minute in tempMinutes.keys():
				tempMinutes[minute] += normDollarVol
			else:
				tempMinutes[minute] = normDollarVol
                else:
			tempMinutes = {}	
			tempMinutes[minute] = normDollarVol
			stocks[stock] = tempMinutes
                        
	return stocks
		


'''This method calculates the difference in stocks and market for each min compared to the previous minute. This gives an idea of how closely the individual stock and the market move'''
def calculateDifference (marketCapital, stocks):
	marketDiff = {}
	stocksDiff = {}
	startTime = 1000
	prev = 1.0
	#calculate market difference/trend
	for key, val in marketCapital.items():
		if key == startTime:
			prev = val
			marketDiff[key] = 1
		else:
			marketDiff[key] = (val - prev)/prev
			prev = val

	#calculate trend for each stock
	for stock, minutes in stocks.items():
		tempMin = {}
		for minute, val in minutes.items():
			if minute == startTime:
				prev = val
				tempMin[minute] = 1
			else:
				tempMin[minute] = (val - prev)/prev
				prev = val
		stocksDiff[stock] = tempMin
	
	return marketDiff, stocksDiff	
				




	#count = 0
	#for i in range(0, len(reader)):
	#	date = dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16, 0, 0)
	#	buy_or_sell = row[4]
	#	quantity = float(row[5])
	#	count = count+1
	#	#yval = (price[i-1]-price[i])/price[i-1]
	#        orders.append([date, symbol, buy_or_sell, quantity])
	#	yvals.append([yval])


if __name__=='__main__':
	
#	transactions = []

	# gets the list of all the csv files of stocks in the directory
	#files = getFileNames()
#	print files

	#
#	transactions = getdata(files)
	
	market_capital, norm_market_capital = createMarketFile(ofile)
	#writeMarketFile(norm_market_capital)
	'''
	writer = csv.writer(open ("market_capital.csv", 'wb'))	
	for key, value  in market_capital.items():
		writer.writerow([key, value])
	'''
	
	stocks = stockMarketCapitalMinute()
	#print norm_market_capital
	marketDiff, stocksDiff = calculateDifference(norm_market_capital, stocks)
	print stocksDiff['cck']
	#model = np.linalg.lstsq(orders, yvals)[0]		

