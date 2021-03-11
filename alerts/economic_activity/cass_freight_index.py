# CASS Freight Index

# Import default libs
import requests, sys, os
from datetime import datetime
import pandas as pd
# Import custom libs
# Allow /lib folder contents to be imported
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from notification_twitter import notification
from api_keys import quandl_api_key
from alert_library import loadPickle, savePickle

# Load save file
saveFile = 'cass_freight_index.pickle'
lastAvailableDate = loadPickle(saveFile)

# Pull data from URL
url = "https://www.quandl.com/api/v3/datasets/CASS/CFI.json?api_key=" + quandl_api_key
response = requests.request("GET", url)
responseJson = response.json()

# Get date of last update
newestAvailableDate = datetime.strptime(responseJson['dataset']['newest_available_date'], '%Y-%m-%d') 
newestAvailableDateAsString = responseJson['dataset']['newest_available_date']

# If there has been an update:
if lastAvailableDate < newestAvailableDate:
	newestData = responseJson['dataset']['data'][0]
	lastData = responseJson['dataset']['data'][1]
	lastQuarterData = responseJson['dataset']['data'][3]
	lastYearData = responseJson['dataset']['data'][12]
	# Data legend, for newestData, lastData, etc:
	# [0]="Date"
	# [1]="Shipments Index"
	# [2]="Expenditures Index"

	# Send tweet    
	tweet = f'CASS Freight Index - Shipments, {newestAvailableDateAsString}: {newestData[1]}\n\n\
1m ago: {lastData[1]} (MoM: {(float(newestData[1]) - float(lastData[1])) / float(lastData[1]) * 100:.1f}%)\n\
1q ago: {lastQuarterData[1]} (QoQ: {(float(newestData[1]) - float(lastQuarterData[1])) / float(lastQuarterData[1]) * 100:.1f}%)\n\
1y ago: {lastYearData[1]} (YoY: {(float(newestData[1]) - float(lastYearData[1])) / float(lastYearData[1]) * 100:.1f}%)\n\n\
Freight Expenditures, {newestAvailableDateAsString}: {newestData[2]}\n\n\
1m: {lastData[2]} (MoM: {(float(newestData[2]) - float(lastData[2])) / float(lastData[2]) * 100:.1f}%)\n\
1q: {lastQuarterData[2]} (QoQ: {(float(newestData[2]) - float(lastQuarterData[2])) / float(lastQuarterData[2]) * 100:.1f}%)\n\
1y: {lastYearData[2]} (YoY: {(float(newestData[2]) - float(lastYearData[2])) / float(lastYearData[2]) * 100:.1f}%)'
	notification(tweet) 

	# Write CSV file
	if os.path.exists('cass_freight_index.csv'):
		df = pd.read_csv('cass_freight_index.csv')

		for month in responseJson['dataset']['data']: # if there is a datapoint ("month") that is not in csv, add it
			if month[0] not in df.index:
				df.loc[month[0]] = [[month[1], month[2]]]
		df.to_csv('cass_freight_index.csv')

	else:
		# add all datapoints in json to csv
		index = []
		shipments_index = []
		expenditures_index = []
		for month in responseJson['dataset']['data']:
			index.append(month[0])
			shipments_index.append(month[1])
			expenditures_index.append(month[2])
		df = pd.DataFrame(index=index,columns=['shipments_index', 'expenditures_index'])
		df['shipments_index'] = shipments_index
		df['expenditures_index'] = expenditures_index
		df.to_csv('cass_freight_index.csv')

	
else:
	print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

savePickle(saveFile, newestAvailableDate)