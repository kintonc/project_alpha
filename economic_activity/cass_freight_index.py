import requests
import json
from datetime import datetime
from notification_twitter import notification
import pandas as pd
import os.path
import pickle
import urllib
from api_keys import quandl_api_key
from alert_library import loadPickle, savePickle

url = "https://www.quandl.com/api/v3/datasets/CASS/CFI.json?api_key=" + quandl_api_key

response = requests.request("GET", url)
responseJson = response.json()
newestAvailableDate = datetime.strptime(responseJson['dataset']['newest_available_date'],
                               '%Y-%m-%d') # newest available date for rail data
newestAvailableDateAsString = responseJson['dataset']['newest_available_date']

# Data legend:
# 0="Date"
# 1="Shipments Index"
# 2="Expenditures Index"

saveFile = 'cass_freight_index.pickle'
lastAvailableDate = loadPickle(saveFile)

# If AAII Sentiment Data has been updated:
if lastAvailableDate < newestAvailableDate:
    newestData = responseJson['dataset']['data'][0]
    lastData = responseJson['dataset']['data'][1]
    lastQuarterData = responseJson['dataset']['data'][3]
    lastYearData = responseJson['dataset']['data'][12]
    
    tweet = f'CASS Freight Index - Shipments, {newestAvailableDateAsString}: {newestData[1]}\n\n\
1m ago: {lastData[1]} (MoM: {(float(newestData[1]) - float(lastData[1])) / float(lastData[1]) * 100:.1f}%)\n\
1q ago: {lastQuarterData[1]} (QoQ: {(float(newestData[1]) - float(lastQuarterData[1])) / float(lastQuarterData[1]) * 100:.1f}%)\n\
1y ago: {lastYearData[1]} (YoY: {(float(newestData[1]) - float(lastYearData[1])) / float(lastYearData[1]) * 100:.1f}%)\n\n\
Freight Expenditures, {newestAvailableDateAsString}: {newestData[2]}\n\n\
1m: {lastData[2]} (MoM: {(float(newestData[2]) - float(lastData[2])) / float(lastData[2]) * 100:.1f}%)\n\
1q: {lastQuarterData[2]} (QoQ: {(float(newestData[2]) - float(lastQuarterData[2])) / float(lastQuarterData[2]) * 100:.1f}%)\n\
1y: {lastYearData[2]} (YoY: {(float(newestData[2]) - float(lastYearData[2])) / float(lastYearData[2]) * 100:.1f}%)'
    
    notification(tweet) 
    
else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

savePickle(saveFile, newestAvailableDate)