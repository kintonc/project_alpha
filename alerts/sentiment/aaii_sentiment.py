# AAII Sentiment

import pandas as pd
import requests
from datetime import datetime
import sys, os
# Allow /lib folder contents to be imported
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from notification_twitter import notification
from alert_library import loadPickle, savePickle
from api_keys import quandl_api_key


# Load save file
saveFile = 'aaii_sentiment.pickle'
lastAvailableDate = loadPickle(saveFile)

# Pull data from URL
url = "https://www.quandl.com/api/v3/datasets/AAII/AAII_SENTIMENT.json?api_key=" + quandl_api_key
response = requests.request("GET", url)
responseJson = response.json()

# Get date of last update
newestAvailableDate = datetime.strptime(responseJson['dataset']['newest_available_date'], '%Y-%m-%d') 
newestAvailableDateAsString = responseJson['dataset']['newest_available_date']

# If there has been an update:
if lastAvailableDate < newestAvailableDate:
	# Get data
	newestData = responseJson['dataset']['data'][0]
	lastData = responseJson['dataset']['data'][1]

	# Calculate Moving Averages    
	bullishMovingAvg = neutralMovingAvg = bearishMovingAvg = bullBearSpreadMovingAvg = 0
	spyEightWeekHigh = spyEightWeekLow = spyEightWeekCloseMovingAvg = 0

	for i in range(0,8):
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


	# Send tweet
	tweet = f'AAII Sentiment, {newestAvailableDateAsString}\n\n\
Bullish: {newestData[1]*100:.1f}, {lastData[1]*100:.1f}, {bullishMovingAvg*100:.1f}\n\
Neutral: {newestData[2]*100:.1f}, {lastData[2]*100:.1f}, {neutralMovingAvg*100:.1f}\n\
Bearish: {newestData[3]*100:.1f}, {lastData[3]*100:.1f}, {bearishMovingAvg*100:.1f}\n\
Bull Bear Spread: {newestData[6]*100:.1f}, {lastData[6]*100:.1f}, {bullBearSpreadMovingAvg*100:.1f}\n\
SPX Wkly High: {round(newestData[10])}, {round(lastData[10])}, {round(spyEightWeekHigh)} (8 wk high)\n\
SPX Wkly Low: {round(newestData[11])}, {round(lastData[11])}, {round(spyEightWeekLow)} (8 wk low)\n\
SPX Wkly Close: {round(newestData[12])}, {round(lastData[12])}, {round(spyEightWeekCloseMovingAvg)}'
	notification(tweet)    

	# Write CSV file
	if os.path.exists('aaii_sentiment.csv'):
		df = pd.read_csv('aaii_sentiment.csv')

		for week in responseJson['dataset']['data']: # if there is a datapoint ("weej") that is not in csv, add it
			if week[0] not in df.index:
				df.loc[week[0]] = [week[1], week[2], week[3], week[6], week[10], week[11], week[12]]
		df.to_csv('aaii_sentiment.csv')

	else:
		# add all datapoints in json to csv
		index = []
		data = []
		for week in responseJson['dataset']['data']:
			index.append(week[0])
			data.append([week[1], week[2], week[3], week[6], week[10], week[11], week[12]])
		df = pd.DataFrame(data, index=index,columns=['bullish','neutral','bearish','bull_bear_spread_moving_avg','spy_weekly_high','spy_weekly_low','spy_weekly_close'])
		df.to_csv('aaii_sentiment.csv')
	
else:
	print('Not updated, no new data, last data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

# Update save file
savePickle(saveFile, newestAvailableDate)