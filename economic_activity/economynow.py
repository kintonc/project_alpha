import pandas as pd
from datetime import datetime, timedelta
import os
from notification_twitter import notification
import re
import pickle
from alert_library import loadPickle, savePickle, retrieveDOM


# Load save file
saveFile = 'economynow.pickle'
lastAvailableDate = loadPickle(saveFile)

    
# parameters
url = "https://www.frbatlanta.org/cqer/research/gdpnow"
dom = retrieveDOM(url)

# Xpath code
xpathCode = '/html/body/div[1]/div/div[2]/div/div[2]/div/div/div/div[2]/div/div[1]/div[1]/h3//text()'
result = dom.xpath(xpathCode)
print(result)

for i in range(len(result)):
    result[i] = result[i].replace('\n','')
    
result[0] = result[0].replace('Latest estimate:','')
result[1] = result[1].replace(' percent —','')

# reorder result array, so that estimate date comes first
reorderIndices = [1,0]
result = [result[i] for i in reorderIndices]


# Create dataframe
df = pd.DataFrame(result).transpose()
df.columns=['date_of_estimate','pct_growth']

newestAvailableDate = datetime.strptime(result[0],'%B %d, %Y')
newestAvailableDate = newestAvailableDate + timedelta(hours=23,minutes=59,seconds=59)
newestAvailableDateAsStr = newestAvailableDate.strftime('%Y-%m-%d')
pctGrowth = result[1]

print('Newest Available Date: ' + newestAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

if lastAvailableDate < newestAvailableDate:    
    tweet = f"US GDP Economy Now - {newestAvailableDateAsStr}\n\
Next qtr: {pctGrowth}%"

    notification(tweet)
    
    if os.path.isfile('economynow.csv'):
        df.to_csv('economynow.csv', mode='a', header=False)
    else: # If .csv file doesn't exist yet
        df.to_csv('economynow.csv')
    
    
else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

# Update save file
savePickle(saveFile, newestAvailableDate)