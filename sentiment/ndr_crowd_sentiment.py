import pandas as pd
from datetime import datetime
import os
from notification_twitter import notification
import re
import pickle
from alert_library import loadPickle, savePickle, retrieveDOM

# Load save file
saveFile = 'ndr_crowd_sentiment.pickle'
lastAvailableDate = loadPickle(saveFile)
    
# parameters
url = "https://www.ndr.com/invest/infopage/S574"

# XPATH
dom = retrieveDOM(url)

# XPath code to grab date table
resultDate = dom.xpath('/html/body/pre/span//text()')

# Xpath code to grab latest update date
newestAvailableDateAsStr = dom.xpath('/html/body/table/tbody/tr[2]/td[2]/b//text()')[0]
#print(newestAvailableDateAsStr)
newestAvailableDate = datetime.strptime(newestAvailableDateAsStr, '%Y-%m-%d')
print('newest available date of data: ' + newestAvailableDateAsStr)

# Extract dates and Sentiments
# Regex match for date (##-##-####) i.e. (mm-dd-yyyy)
dates = re.findall(r'\d{2}/\d{2}/\d{4}', resultDate[0])
# Get crowd sentiment numbers, by looking only at the text to the right of "NDR Crowd Sentiment" (hence [1])
crowdSentimentStr = resultDate[0].split('NDR Crowd Sentiment')[1]
# Regex match for sentiment numbers (##.###)
crowdSentiment = re.findall(r'\d{2}.\d{3}', crowdSentimentStr)
#print(dates)
#print(crowdSentiment)

# Create dataframe, with dates and sentiment
df = pd.DataFrame({'date': dates, 'ndr_crowd_sentiment': crowdSentiment})
# Convert dates from mm-dd-yyyy to yyyy-mm-dd
df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
df['ndr_crowd_sentiment'] = pd.to_numeric(df['ndr_crowd_sentiment'])

# If there has been an update:
if lastAvailableDate < newestAvailableDate:    
    tweet = f"NDR Crowd Sentiment - {newestAvailableDateAsStr}\n\
5-day MA: {df['ndr_crowd_sentiment'].mean():.3f}\n\n"

    # Add data from each day to tweet
    for indexNum in df.index:
        tweet += f"{df['date'][indexNum]}: {df['ndr_crowd_sentiment'][indexNum]:.3f}\n"
        
    notification(tweet)
    
    # Sort dataframe to be ascending order, based on date
    df = df.sort_values(by='date')
    # If there was a data update, then append to .csv file
    if os.path.isfile('ndr_crowd_sentiment.csv'):
        df.to_csv('ndr_crowd_sentiment.csv', mode='a', header=False)
    else: # If .csv file doesn't exist yet
        df.to_csv('ndr_crowd_sentiment.csv')
    
    
else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

# Update save file
savePickle(saveFile, newestAvailableDate)