# T10 minus T2 spread - daily

import pandas as pd
from datetime import datetime, timedelta
from notification_twitter import notification
from alert_library import loadPickle, savePickle
from alert_library_fred import getValueFromCSV, verifyDates


# Load save file
saveFile = 'fred_t10-t2_spread.pickle'
lastAvailableDate = loadPickle(saveFile)

dates = {
    'twoYearsOneMonthAgo': datetime.now() - timedelta(days=760),
    'twoYearsAgo': datetime.now() - timedelta(days=730),
    'today': datetime.now()    
}

# parameters
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10Y2Y\
&cosd=" + dates['twoYearsOneMonthAgo'].strftime('%Y-%m-%d') + \
"&coed=" + dates['today'].strftime('%Y-%m-%d')

csv = pd.read_csv(url)
print(csv)

# get last date in CSV
lastDate = datetime.strptime(csv['DATE'].iloc[-1],'%Y-%m-%d')

dates['twoYearsAgo'] = (lastDate - timedelta(days=730)).date()
dates['oneYearAgo'] = (lastDate - timedelta(days=365)).date()
dates['sixMonthsAgo'] = (lastDate - timedelta(days=182)).date()
dates['threeMonthsAgo'] = (lastDate - timedelta(days=91)).date()
dates['oneMonthAgo'] = (lastDate - timedelta(days=30)).date()
dates['twoWeeksAgo'] = (lastDate - timedelta(days=14)).date()
dates['oneWeekAgo'] = (lastDate - timedelta(days=7)).date()
dates['yesterday'] = (lastDate - timedelta(days=1)).date()
dates['today'] = lastDate.date()

dates = verifyDates(csv,dates,'DATE','T10Y2Y')

values = {
    'twoYearsAgo': getValueFromCSV(csv,dates['twoYearsAgo'].strftime('%Y-%m-%d'),'DATE','T10Y2Y'),
    'oneYearAgo': getValueFromCSV(csv,dates['oneYearAgo'].strftime('%Y-%m-%d'),'DATE','T10Y2Y'),
    'sixMonthsAgo': getValueFromCSV(csv,dates['sixMonthsAgo'].strftime('%Y-%m-%d'),'DATE','T10Y2Y'),
    'threeMonthsAgo': getValueFromCSV(csv,dates['threeMonthsAgo'].strftime('%Y-%m-%d'),'DATE','T10Y2Y'),
    'oneMonthAgo': getValueFromCSV(csv,dates['oneMonthAgo'].strftime('%Y-%m-%d'),'DATE','T10Y2Y'),
    'twoWeeksAgo': getValueFromCSV(csv,dates['twoWeeksAgo'].strftime('%Y-%m-%d'),'DATE','T10Y2Y'),
    'oneWeekAgo': getValueFromCSV(csv,dates['oneWeekAgo'].strftime('%Y-%m-%d'),'DATE','T10Y2Y'),
    'yesterday': getValueFromCSV(csv,dates['yesterday'].strftime('%Y-%m-%d'),'DATE','T10Y2Y'),
    'today': getValueFromCSV(csv,dates['today'].strftime('%Y-%m-%d'),'DATE','T10Y2Y'),
}

if lastAvailableDate < lastDate:    
    tweet = f"US 10Y-2Y Treasury Yield - {lastDate.strftime('%Y-%m-%d')}: {values['today']}%\n\
1d: {values['yesterday']}% ({((values['today']-values['yesterday'])/values['yesterday'])*100:.1f}%)\n\
1w: {values['oneWeekAgo']}% ({((values['today']-values['oneWeekAgo'])/values['oneWeekAgo'])*100:.1f}%)\n\
2w: {values['twoWeeksAgo']}% ({((values['today']-values['twoWeeksAgo'])/values['twoWeeksAgo'])*100:.1f}%)\n\
1m: {values['oneMonthAgo']}% ({((values['today']-values['oneMonthAgo'])/values['oneMonthAgo'])*100:.1f}%)\n\
3m: {values['threeMonthsAgo']}% ({((values['today']-values['threeMonthsAgo'])/values['threeMonthsAgo'])*100:.1f}%)\n\
6m: {values['sixMonthsAgo']}% ({((values['today']-values['sixMonthsAgo'])/values['sixMonthsAgo'])*100:.1f}%)\n\
1y: {values['oneYearAgo']}% ({((values['today']-values['oneYearAgo'])/values['oneYearAgo'])*100:.1f}%)\n\
2y: {values['twoYearsAgo']}% ({((values['today']-values['twoYearsAgo'])/values['twoYearsAgo'])*100:.1f}%)"

    notification(tweet)
        
else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

# Update save file
savePickle(saveFile, lastDate)