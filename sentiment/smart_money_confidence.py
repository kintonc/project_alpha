from selenium import webdriver
from bs4 import BeautifulSoup
from pprint import *
from lxml import etree
import pandas as pd
from datetime import datetime
import os
import pickle
from notification_twitter import notification
from alert_library import loadPickle, savePickle, retrieveDOM

# Load save file
saveFile = 'smart_money_confidence.pickle'
lastAvailableDate = loadPickle(saveFile)
    
# parameters
url = "https://sentimentrader.com/smart-money/"

# XPATH
dom = retrieveDOM(url)

# Xpath code
xpathCode = '/html/body/script[2]/text()'
result = dom.xpath(xpathCode)

# Manipulate strings and lists as needed
resultAsStr = result[0].split("chart_data.data = ",1)[1]
resultAsStr = resultAsStr.replace("[[", "")
resultAsStr = resultAsStr.replace("]];", "")
resultAsStr = resultAsStr.replace("\'", "")
resultAsStr = resultAsStr.replace("\n", "")
resultAsStr = resultAsStr.replace(" ", "")
resultAsStr += ']'

# create new temporary list to split resultAsStr by '],[' into lists
tempList = resultAsStr.split('],[') 
dataList = [] # to store data

# split list into lists of lists (so that you can convert list of lists into dataframe)
for i in range(0,len(tempList)):
    tempList[i] = tempList[i].replace("]", "")
    dataList.append(tempList[i].split(','))

df = pd.DataFrame(dataList, columns=['date','smart','spx','dumb'])
df['date'] = pd.to_datetime(df['date'],unit='ms')

newestAvailableDate = df.iloc[len(df)-1]['date']
newestAvailableDateAsStr = datetime.strftime(newestAvailableDate, '%Y-%m-%d')

if lastAvailableDate < newestAvailableDate:
    thisMth = df.iloc[len(df)-1]
    lastMth = df.iloc[len(df)-2]
    lastQtr = df.iloc[len(df)-4]
    lastYr = df.iloc[len(df)-13]
    
    tweet = f"Smart/Dumb Money Confidence - {newestAvailableDateAsStr}\n\
Smart: {thisMth['smart']}\n\n\
1 mth ago: {lastMth['smart']} (MoM: {(float(lastMth['smart']) - float(thisMth['smart'])) / float(thisMth['smart']) * 100:.1f}%)\n\
1 qtr ago: {lastQtr['smart']} (QoQ: {(float(lastQtr['smart']) - float(thisMth['smart'])) / float(thisMth['smart']) * 100:.1f}%)\n\
1 yr ago: {lastYr['smart']} (YoY: {(float(lastYr['smart']) - float(thisMth['smart'])) / float(thisMth['smart']) * 100:.1f}%)\n\n\
Dumb: {thisMth['dumb']}\n\n\
1 mth ago: {lastMth['dumb']} (MoM: {(float(lastMth['dumb']) - float(thisMth['dumb'])) / float(thisMth['dumb']) * 100:.1f}%)\n\
1 qtr ago: {lastQtr['dumb']} (QoQ: {(float(lastQtr['dumb']) - float(thisMth['dumb'])) / float(thisMth['dumb']) * 100:.1f}%)\n\
1 yr ago: {lastYr['dumb']} (YoY: {(float(lastYr['dumb']) - float(thisMth['dumb'])) / float(thisMth['dumb']) * 100:.1f}%)"
    
    notification(tweet)
    
else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

savePickle(saveFile, newestAvailableDate)
      
df.to_csv('smart_dumb_money_confidence.csv')