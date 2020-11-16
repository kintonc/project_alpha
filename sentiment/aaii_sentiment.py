import json
import requests
from datetime import datetime
from notification_twitter import notification
import pandas as pd
import os.path
import pickle
import urllib
from alert_library import loadPickle, savePickle
from api_keys import quandl_api_key


url = "https://www.quandl.com/api/v3/datasets/AAII/AAII_SENTIMENT.json?api_key=" + quandl_api_key
response = requests.request("GET", url)
responseJson = response.json()
newestAvailableDate = datetime.strptime(responseJson['dataset']['newest_available_date'],
                               '%Y-%m-%d') # newest available date for the AAII data
newestAvailableDateAsString = responseJson['dataset']['newest_available_date']

# Data legend:
# 0="Date"
# 1="Bullish"
# 2="Neutral"
# 3="Bearish"
# 4="Total"
# 5="Bullish 8-Week Mov Avg"
# 6="Bull-Bear Spread"
# 7="Bullish Average"
# 8="Bullish Average + St. Dev"
# 9="Bullish Average - St. Dev"
# 10="S&P 500 Weekly High"
# 11="S&P 500 Weekly Low"
# 12="S&P 500 Weekly Close"

saveFile = 'aaii.pickle'
lastAvailableDate = loadPickle(saveFile)

# Calculate Moving Averages    
bullishMovingAvg = 0 # column = 1
neutralMovingAvg = 0 # column = 2
bearishMovingAvg = 0 # column = 3
bullBearSpreadMovingAvg = 0 # column = 6
spyEightWeekHigh = 0 # column = 10
spyEightWeekLow = 0 # col = 11
spyEightWeekCloseMovingAvg = 0 # col = 12

for i in range(0,8):
    bullishMovingAvg += responseJson['dataset']['data'][i][1]
    neutralMovingAvg += responseJson['dataset']['data'][i][2]
    bearishMovingAvg += responseJson['dataset']['data'][i][3]
    bullBearSpreadMovingAvg += responseJson['dataset']['data'][i][6]
    spyEightWeekHigh = max(responseJson['dataset']['data'][i][10], spyEightWeekHigh)
    spyEightWeekLow = max(responseJson['dataset']['data'][i][11], spyEightWeekLow)
    spyEightWeekCloseMovingAvg += responseJson['dataset']['data'][i][12]
    
bullishMovingAvg /= 8
neutralMovingAvg /= 8
bearishMovingAvg /= 8
bullBearSpreadMovingAvg /= 8 
spyEightWeekCloseMovingAvg /= 8 

print(lastAvailableDate)
# If AAII Sentiment Data has been updated:
if lastAvailableDate < newestAvailableDate:
    newestData = responseJson['dataset']['data'][0]
    lastData = responseJson['dataset']['data'][1]
    
    tweet = f'AAII Sentiment, {newestAvailableDateAsString}\n\n\
Bullish: {newestData[1]*100:.1f}, {lastData[1]*100:.1f}, {bullishMovingAvg*100:.1f}\n\
Neutral: {newestData[2]*100:.1f}, {lastData[2]*100:.1f}, {neutralMovingAvg*100:.1f}\n\
Bearish: {newestData[3]*100:.1f}, {lastData[3]*100:.1f}, {bearishMovingAvg*100:.1f}\n\
Bull Bear Spread: {newestData[6]*100:.1f}, {lastData[6]*100:.1f}, {bullBearSpreadMovingAvg*100:.1f}\n\
SPX Wkly High: {round(newestData[10])}, {round(lastData[10])}, {round(spyEightWeekHigh)} (8 wk high)\n\
SPX Wkly Low: {round(newestData[11])}, {round(lastData[11])}, {round(spyEightWeekLow)} (8 wk low)\n\
SPX Wkly Close: {round(newestData[12])}, {round(lastData[12])}, {round(spyEightWeekCloseMovingAvg)}'
    
    notification(tweet)    
    
else:
    print('Not updated, no new data, last data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

# Update save file
savePickle(saveFile, newestAvailableDate)   