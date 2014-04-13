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
import pickle

dayFile = "day2.csv"
startTime = 1000
threshold = 10
pickleFile = "dayfile.p"
dayData = []


def serialize (dayFile):
	lines = []
	reader = csv.reader( open (dayFile, 'rb'))
	for row in reader:
		lines.append(row)
	pickle.dump( lines, open( pickleFile, "wb" ) )


def deserialize (pickleFile):
	dayData = pickle.load( open( pickleFile, "rb" ) )
	return dayData


def getChangeInMarket(dayData):
        marketChange = {}
	marketDollarVol = {}
        for row in dayData:
		date = str(row[0])
                minute = int(row[1])
		key = (date, minute)
                if key in marketDollarVol.keys():
                        marketDollarVol[key] += float(row[5])*float(row[6])
                else:
                        marketDollarVol[key] = float(row[5])*float(row[6])

        #sort the market capital and take percentage change compared to the previous day
        sortedDollarVol = collections.OrderedDict(sorted(marketDollarVol.items()))
	prev = 1
	#The value for 1000 gets added to the dictionary too but it should not be used
        for key,val in sortedDollarVol.items():
		if key[1] == startTime:
			prev = val
			marketChange[key] = 0.0
		else:
			marketChange[key] = float((val-prev)/prev)
			prev = val
	sortedMarketChange = collections.OrderedDict(sorted(marketChange.items()))
	return sortedMarketChange



def getChangeInStocks(dayData):
	stocks = {}
	stockChange = {}
	minuteDollarVol = {}
	for row in dayData:
                stock = row[10]
                minute = int(row[1])
		date = str(row[0])
		key = (date, minute)
                dollarVol = float(row[5])*float(row[6])
		if stock in stocks.keys():
                        tempMinutes = stocks[stock]
                        if key in tempMinutes.keys():
				tempMinutes[key] += dollarVol
			else:
				tempMinutes[key] = dollarVol
		else:
			tempMinutes = {}
                        tempMinutes[key] = dollarVol
			minutes = collections.OrderedDict(sorted(tempMinutes.items()))
                        stocks[stock] = minutes
	
	#calculate the percentage in dollar volume for each min compared to the previoud minute
	for stock, minutes in stocks.items():
		change = {}
		prev = 1
		for key,val in minutes.items():
                	if key[1] == startTime:
                        	prev = val
                        	change[key] = 0.0
                	else:
                        	change[key] = float((val-prev)/prev)
                        	prev = val
		sortedChange = collections.OrderedDict(sorted(change.items()))
		stockChange[stock] = sortedChange
	return stockChange




def getTrend (marketChange, stockChange):
	orders = []
	impTimes = []
	impStocks = []
	for stock, minuteChange in stockChange.items():
		for time, stockVal in minuteChange.items():
			marketVal = marketChange[time]
			if float(abs(stockVal-marketVal)) >= threshold:
				if float(stockVal - marketVal)>0:
					orders.append([key[0], key[1],  
				impTimes.append(int(time))
				impStocks.append(stock)		

	return impTimes, impStocks

	


if __name__ == '__main__':
	#serialize(dayFile)
	dayData = deserialize(pickleFile)
	'''
	marketChange = getChangeInMarket(dayFile)
	print marketChange				
	stockChange = getChangeInStocks(dayFile)
	
	impTimes, impStocks = getTrend (marketChange, stockChange)
	#print impTimes, impStocks
	'''





	
