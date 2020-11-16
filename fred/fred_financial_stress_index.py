# Fed Financial Stress Index - weekly on Fridays

import pandas as pd
from datetime import datetime, timedelta
from notification_twitter import notification
from alert_library import loadPickle, savePickle
from alert_library_fred import getValueFromCSV, verifyDates

# Load save file
saveFile = 'fred_financial_stress_index.pickle'
lastAvailableDate = loadPickle(saveFile)

# Find last Friday
dates = {}

dates['today'] = datetime.now()
oneday = timedelta(days=1)

while dates['today'].isoweekday() != 5:
    dates['today'] -= oneday

dates['twoYearsOneMonthAgo'] = dates['today'] - timedelta(days=760)
dates['twoYearsAgo'] = dates['today'] - timedelta(days=728)

# parameters
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=STLFSI2\
&cosd=" + dates['twoYearsOneMonthAgo'].strftime('%Y-%m-%d') + \
"&coed=" + dates['today'].strftime('%Y-%m-%d')

csv = pd.read_csv(url)
print(csv)

# get last date in CSV
lastDate = datetime.strptime(csv['DATE'].iloc[-1],'%Y-%m-%d')

dates['twoYearsAgo'] = (lastDate - timedelta(days=728)).date()
dates['oneYearAgo'] = (lastDate - timedelta(days=364)).date()
dates['sixMonthsAgo'] = (lastDate - timedelta(days=182)).date()
dates['threeMonthsAgo'] = (lastDate - timedelta(days=91)).date()
dates['oneMonthAgo'] = (lastDate - timedelta(days=28)).date()
dates['twoWeeksAgo'] = (lastDate - timedelta(days=14)).date()
dates['oneWeekAgo'] = (lastDate - timedelta(days=7)).date()
#dates['yesterday'] = (lastDate - timedelta(days=1)).date()
dates['today'] = lastDate.date()

# NO verify dates for this function, as this fn only looks at Fridays

values = {
    'twoYearsAgo': getValueFromCSV(csv,dates['twoYearsAgo'].strftime('%Y-%m-%d'),'DATE','STLFSI2'),
    'oneYearAgo': getValueFromCSV(csv,dates['oneYearAgo'].strftime('%Y-%m-%d'),'DATE','STLFSI2'),
    'sixMonthsAgo': getValueFromCSV(csv,dates['sixMonthsAgo'].strftime('%Y-%m-%d'),'DATE','STLFSI2'),
    'threeMonthsAgo': getValueFromCSV(csv,dates['threeMonthsAgo'].strftime('%Y-%m-%d'),'DATE','STLFSI2'),
    'oneMonthAgo': getValueFromCSV(csv,dates['oneMonthAgo'].strftime('%Y-%m-%d'),'DATE','STLFSI2'),
    'twoWeeksAgo': getValueFromCSV(csv,dates['twoWeeksAgo'].strftime('%Y-%m-%d'),'DATE','STLFSI2'),
    'oneWeekAgo': getValueFromCSV(csv,dates['oneWeekAgo'].strftime('%Y-%m-%d'),'DATE','STLFSI2'),
    #'yesterday': getValueFromCSV(csv,dates['yesterday'].strftime('%Y-%m-%d'),'DATE','STLFSI2'),
    'today': getValueFromCSV(csv,dates['today'].strftime('%Y-%m-%d'),'DATE','STLFSI2'),
}


if lastAvailableDate < lastDate:    
    tweet = f"Fed Financial Stress Index - {lastDate.strftime('%Y-%m-%d')}: {values['today']}\n\
1w: {values['oneWeekAgo']} ({((values['today']-values['oneWeekAgo'])/values['oneWeekAgo'])*100:.1f}%)\n\
2w: {values['twoWeeksAgo']} ({((values['today']-values['twoWeeksAgo'])/values['twoWeeksAgo'])*100:.1f}%)\n\
1m: {values['oneMonthAgo']} ({((values['today']-values['oneMonthAgo'])/values['oneMonthAgo'])*100:.1f}%)\n\
3m: {values['threeMonthsAgo']} ({((values['today']-values['threeMonthsAgo'])/values['threeMonthsAgo'])*100:.1f}%)\n\
6m: {values['sixMonthsAgo']} ({((values['today']-values['sixMonthsAgo'])/values['sixMonthsAgo'])*100:.1f}%)\n\
1y: {values['oneYearAgo']} ({((values['today']-values['oneYearAgo'])/values['oneYearAgo'])*100:.1f}%)\n\
2y: {values['twoYearsAgo']} ({((values['today']-values['twoYearsAgo'])/values['twoYearsAgo'])*100:.1f}%)"

    notification(tweet)
        
else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

# Update save file
savePickle(saveFile, lastDate)