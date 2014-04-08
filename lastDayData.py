# Python imports
import datetime as dt
import csv
import os

# 3rd party imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def get_last_day(csv_filename):
    with open(csv_filename,'rb') as f:
        reader = csv.reader(f)
        lastday = []
        for line in reader:
            if line[0]=='20140314':
                lastday.append(line)
    
    wr=open('lastday_aapl.csv','wb')
    writer = csv.writer(wr,delimiter=',')
    writer.writerow(lastday)
    wr.close()

    return lastday
