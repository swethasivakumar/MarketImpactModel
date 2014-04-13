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
import matplotlib.pyplot as plt


dayFile = "day2.csv"
#dayFile = "sample.csv"
startTime = 1000
threshold = 0.2
#pickleFile = "dayfileDictSample.p"
pickleFile = "dayfile.p"
orderFile = "orders.csv"
#orderFile = "sampleorder.csv"
dayData = []
xTime = []
yMarket = []
yStock = []

#Create a dictionary by reading the csv file once and serialize it so that we don't have to read the csv file each time we want some data. The dictionary has (date, time) as the key and the whole row in the csv file (including date time) as the value. This is needed because we need all the details while creating the significant orders list.

def serialize (dayFile):
	data = {}
	reader = csv.reader( open (dayFile, 'rb'))
	for row in reader:
		if row[0].startswith('\xef\xbb\xbf'):
			row[0] = row[0][3:]
		date = str(row[0])
		time = int(row[1])
		if time not in xTime:
			xTime.append(time)
			xTime.sort()
		stock = str(row[10])
		data[(date, time, stock)] = row
	sortedData = collections.OrderedDict(sorted(data.items()))
	pickle.dump( sortedData, open( pickleFile, "wb" ) )


def deserialize (pickleFile):
	dayData = pickle.load( open( pickleFile, "rb" ) )
	return dayData


def getChangeInMarket(dayData):
        marketChange = {}
	marketDollarVol = {}
        for key, value in dayData.items():
                minute = (str(key[0]), int(key[1]))
		print minute
                if minute in marketDollarVol.keys():
                        marketDollarVol[minute] += float(value[5])*float(value[6])
                else:
                        marketDollarVol[minute] = float(value[5])*float(value[6])

        #sort the market capital and take percentage change compared to the previous day
        sortedDollarVol = collections.OrderedDict(sorted(marketDollarVol.items()))
	#print 'sorted dollar vol', sortedDollarVol
	print "wrong length", len(sortedDollarVol)
	print sortedDollarVol
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
	#print 'sorted market change', sortedMarketChange
	for key, val in sortedMarketChange.items():
                yMarket.append(val)
	return sortedMarketChange



def getChangeInStocks(dayData):
	stocks = {}
	stockChange = {}
	minuteDollarVol = {}
	for key, value in dayData.items():
                stock = key[2]
		#print 'stock', stock
		tempKey = (key[0], key[1])
                dollarVol = float(value[5])*float(value[6])
		if stock in stocks.keys():
                        tempMinutes = stocks[stock]
                        if tempKey in tempMinutes.keys():
				tempMinutes[tempKey] += dollarVol
			else:
				tempMinutes[tempKey] = dollarVol
			
		else:
			tempMinutes = {}
                        tempMinutes[tempKey] = dollarVol
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
	temp = stockChange['aapl']
        for key, val in temp.items():
                yStock.append(val)
	return stockChange




def getTrend (marketChange, stockChange):
	orders = []
	transaction = ''
	for stock, minuteChange in stockChange.items():
		for time, stockVal in minuteChange.items():
			key = (time[0], time[1], stock)
			marketVal = marketChange[time]
			#print stockVal, marketVal
			#print 'market val', marketVal
			#print 'diff', float(abs(stockVal-marketVal))
			if float(abs(stockVal-marketVal)) >= threshold:
				if float(stockVal - marketVal)>0:
					transaction = 'BUY'
				else:
					transaction = 'SELL'
				order = dayData[key]
				order.append(transaction)
				orders.append(order)
	#print orders
				
	return orders


def scatterPlot(xTime, yDollarvolume, yStock):
	fig = plt.figure()
	xTime1 = xTime
	ax1 = fig.add_subplot(111)
	ax1.scatter(xTime, yDollarvolume, s=10, c='b', marker="s", label='market')
	ax1.scatter(xTime1, yStock, s=10, c='r', marker="o", label='aapl')
	plt.legend(loc='upper left');
	plt.show()


def lineplot(x,y1,y2):
	print 'x and ys', x, y1, y2
        plt.gca().set_color_cycle(['red', 'green'])
        plt.plot(x, y1)
        plt.plot(x, y2)
        plt.legend(['market', 'aapl'], loc='upper left')
        plt.show()



def createOrderFile (orders):
	writer = csv.writer(open (orderFile, 'wb'))
	for line in orders:
		writer.writerow(line)
	


if __name__ == '__main__':
	serialize(dayFile)
	dayData = deserialize(pickleFile)
	marketChange = getChangeInMarket(dayData)		
	stockChange = getChangeInStocks(dayData)
	#print 'market change', marketChange
	#print 'stock change', stockChange	
	orders = getTrend (marketChange, stockChange)
	createOrderFile (orders)
	
	#print xTime, yDollarvolume, yStock
	#print 'sizes', len(xTime), len(yDollarvolume), len(yStock)
	#scatterPlot(xTime, yDollarvolume, yStock)
	lineplot(xTime, yMarket, yStock)




	
