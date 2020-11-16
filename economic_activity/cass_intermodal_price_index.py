# CASS Intermodal Price Index

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

url = "https://www.quandl.com/api/v3/datasets/CASS/CIPI.json?api_key=eyxVSTjsTNiby78azAYe"

response = requests.request("GET", url)
responseJson = response.json()
newestAvailableDate = datetime.strptime(responseJson['dataset']['newest_available_date'],
                               '%Y-%m-%d') # newest available date for rail data
newestAvailableDateAsString = responseJson['dataset']['newest_available_date']

# Data legend:
# 0="Date"
# 1="Shipments Index"
# 2="Expenditures Index"

saveFile = 'cass_intermodal_price_index.pickle'
lastAvailableDate = loadPickle(saveFile)

# If AAII Sentiment Data has been updated:
if lastAvailableDate < newestAvailableDate:
    newestData = responseJson['dataset']['data'][0]
    lastData = responseJson['dataset']['data'][1]
    lastQuarterData = responseJson['dataset']['data'][3]
    lastYearData = responseJson['dataset']['data'][12]
    
    tweet = f'CASS Inermodal Price Index, {newestAvailableDateAsString}: {newestData[1]}\n\n\
1 mth ago: {lastData[1]:.2f} (MoM: {(float(newestData[1]) - float(lastData[1])) / float(lastData[1]) * 100:.1f}%)\n\
1 qtr ago: {lastQuarterData[1]:.2f} (QoQ: {(float(newestData[1]) - float(lastQuarterData[1])) / float(lastQuarterData[1]) * 100:.1f}%)\n\
1 yr ago: {lastYearData[1]:.2f} (YoY: {(float(newestData[1]) - float(lastYearData[1])) / float(lastYearData[1]) * 100:.1f}%)'
    
    notification(tweet)
    
else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

savePickle(saveFile, newestAvailableDate)

