import re, json, sys, os, csv, requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
# Allow /lib folder contents to be imported
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from notification_twitter import notification
from alert_library import loadPickle, savePickle


# Load save file
saveFile = 'smart_money_confidence.pickle'
lastAvailableDate = loadPickle(saveFile)

# Load page
page = requests.get('https://sentimentrader.com/smart-money/')
soup = BeautifulSoup(page.content, 'html.parser')

# Get data
script_tag = soup.select('body > script:nth-child(4)')[0].string
data = re.findall('chart_data.data = .*];', script_tag)[0]

# Clean data so that it can be read as JSON
data = data.replace('chart_data.data = ','')  # delete chart_data tag
data = data[:-1] # delete last character (which is a ;)
data = json.loads(data)

# import JSON data as a dataframe
df = pd.DataFrame(data, columns = ['date', 'smart', 'spy', 'dumb'])
df['date'] = pd.to_datetime(df['date'], unit='ms') # convert unix time (in ms) to datetime

# If we have a new update:
if lastAvailableDate < max(df['date']):
    thisMth = df.iloc[len(df) - 1]
    lastMth = df.iloc[len(df) - 2]
    lastQtr = df.iloc[len(df) - 4]
    lastYr = df.iloc[len(df) - 13]

    tweet = f"Smart/Dumb Money Confidence - {datetime.strftime(max(df['date']), '%Y-%m-%d')}\n\
Smart: {thisMth['smart']}\n\n\
1 mth ago: {lastMth['smart']} (MoM: {(float(lastMth['smart']) - float(thisMth['smart'])) / float(thisMth['smart']) * 100:.1f}%)\n\
1 qtr ago: {lastQtr['smart']} (QoQ: {(float(lastQtr['smart']) - float(thisMth['smart'])) / float(thisMth['smart']) * 100:.1f}%)\n\
1 yr ago: {lastYr['smart']} (YoY: {(float(lastYr['smart']) - float(thisMth['smart'])) / float(thisMth['smart']) * 100:.1f}%)\n\n\
Dumb: {thisMth['dumb']}\n\n\
1 mth ago: {lastMth['dumb']} (MoM: {(float(lastMth['dumb']) - float(thisMth['dumb'])) / float(thisMth['dumb']) * 100:.1f}%)\n\
1 qtr ago: {lastQtr['dumb']} (QoQ: {(float(lastQtr['dumb']) - float(thisMth['dumb'])) / float(thisMth['dumb']) * 100:.1f}%)\n\
1 yr ago: {lastYr['dumb']} (YoY: {(float(lastYr['dumb']) - float(thisMth['dumb'])) / float(thisMth['dumb']) * 100:.1f}%)"

    notification(tweet)

    if os.path.isfile('smart_money_confidence.csv'):
        with open('smart_money_confidence.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(thisMth)
    else:
        with open('smart_money_confidence.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date','smart','spy','dumb'])
            writer.writerows(df)

else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

savePickle(saveFile, max(df['date']))

print(df)

