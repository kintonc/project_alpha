# Fear and Greed index
# Fear and Greed graph from CNN: http://markets.money.cnn.com/Marketsdata/Api/Chart/FearGreedHistoricalImage?chartType=AvgPtileModel

import requests, sys, os, pickle, datetime, csv
# Allow /lib folder contents to be imported
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from notification_twitter import notification
from api_keys import rapidapi_api_key

# Load save file. We cannot use normal "loadPickle" function as this pickle stores different data.
saveFile = 'fear_and_greed.pickle'
if(os.path.isfile(saveFile)):
    with open(saveFile, 'rb') as f:
        lastFGValue = pickle.load(f) # last Fear and Greed value
        lastFGText = pickle.load(f) # last Fear and Greed text ("Fear", "Greed")
        lastRun = pickle.load(f) # datetime of when this script was last run
else:
    lastFGValue = lastFGText = lastRun = 0


# Pull data from URL
url = "https://fear-and-greed-index.p.rapidapi.com/v1/fgi"
headers = {
    'x-rapidapi-host': "fear-and-greed-index.p.rapidapi.com",
    'x-rapidapi-key': rapidapi_api_key
    }
response = requests.request("GET", url, headers=headers)
responseJson = response.json()
responseJson = responseJson['fgi']
#print(json.dumps(responseJson, indent=4)) # print JSON

# Store data in CSV
if os.path.exists('fear_and_greed.csv'):
    with open('fear_and_greed.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), responseJson['now']['value'], responseJson['now']['valueText']])
else:
    with open('fear_and_greed.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp','value','description'])
        writer.writerow([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), responseJson['now']['value'], responseJson['now']['valueText']])

# Send tweet
tweet = f"Fear and Greed Index: {responseJson['now']['value']}, {responseJson['now']['valueText']}\n\n\
Previous: {lastFGValue}, {lastFGText}, {lastRun}\n\
1w ago: {responseJson['oneWeekAgo']['value']}, {responseJson['oneWeekAgo']['valueText']}\n\
1m ago: {responseJson['oneMonthAgo']['value']}, {responseJson['oneMonthAgo']['valueText']}\n\
1y ago: {responseJson['oneYearAgo']['value']}, {responseJson['oneYearAgo']['valueText']}"
notification(tweet)

# Save current values in Pickle
with open(saveFile, 'wb') as f:
    pickle.dump(responseJson['now']['value'], f)
    pickle.dump(responseJson['now']['valueText'], f)
    pickle.dump(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), f)