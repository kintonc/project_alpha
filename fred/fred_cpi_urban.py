#  Consumer Price Index for All Urban Consumers, monthly

import pandas as pd
from datetime import datetime, timedelta
from notification_twitter import notification
from alert_library import loadPickle, savePickle
from alert_library_fred import getValueFromCSV, verifyDates
from dateutil.relativedelta import relativedelta

six_months = datetime.now() + relativedelta(months=+6)

# Load save file
saveFile = 'fred_cpi_urban.pickle'
lastAvailableDate = loadPickle(saveFile)


dates = {}
dates['today'] = datetime.now()
dates['twoYearsOneMonthAgo'] = dates['today'] - relativedelta(months=+30)
dates['twoYearsAgo'] = dates['today'] - relativedelta(months=+24)

# parameters
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL\
&cosd=" + dates['twoYearsOneMonthAgo'].strftime('%Y-%m-%d') + \
"&coed=" + dates['today'].strftime('%Y-%m-%d')

csv = pd.read_csv(url)
print(csv)

# get last date in CSV
lastDate = datetime.strptime(csv['DATE'].iloc[-1],'%Y-%m-%d')

dates['twoYearsAgo'] = (lastDate - relativedelta(months=+24)).date()
dates['oneYearAgo'] = (lastDate - relativedelta(months=+12)).date()
dates['sixMonthsAgo'] = (lastDate - relativedelta(months=+6)).date()
dates['threeMonthsAgo'] = (lastDate - relativedelta(months=+3)).date()
dates['oneMonthAgo'] = (lastDate - relativedelta(months=+1)).date()
#dates['twoWeeksAgo'] = (lastDate - timedelta(days=14)).date()
#dates['oneWeekAgo'] = (lastDate - timedelta(days=7)).date()
#dates['yesterday'] = (lastDate - timedelta(days=1)).date()
dates['today'] = lastDate.date()

# NO Verify needed, as these values are monthly (always on day = 1, ex: Jan 1, Feb 1, etc)

values = {
    'twoYearsAgo': getValueFromCSV(csv,dates['twoYearsAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
    'oneYearAgo': getValueFromCSV(csv,dates['oneYearAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
    'sixMonthsAgo': getValueFromCSV(csv,dates['sixMonthsAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
    'threeMonthsAgo': getValueFromCSV(csv,dates['threeMonthsAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
    'oneMonthAgo': getValueFromCSV(csv,dates['oneMonthAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
    #'twoWeeksAgo': getValueFromCSV(csv,dates['twoWeeksAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
    #'oneWeekAgo': getValueFromCSV(csv,dates['oneWeekAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
    #'yesterday': getValueFromCSV(csv,dates['yesterday'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
    'today': getValueFromCSV(csv,dates['today'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
}




if lastAvailableDate < lastDate:    
    tweet = f" Consumer Price Index for All Urban Consumers - {lastDate.strftime('%Y-%m-%d')}: {values['today']}\n\
1m: {values['oneMonthAgo']:.1f} ({((values['today']-values['oneMonthAgo'])/values['oneMonthAgo'])*100:.1f}%)\n\
3m: {values['threeMonthsAgo']:.1f} ({((values['today']-values['threeMonthsAgo'])/values['threeMonthsAgo'])*100:.1f}%)\n\
6m: {values['sixMonthsAgo']:.1f} ({((values['today']-values['sixMonthsAgo'])/values['sixMonthsAgo'])*100:.1f}%)\n\
1y: {values['oneYearAgo']:.1f} ({((values['today']-values['oneYearAgo'])/values['oneYearAgo'])*100:.1f}%)\n\
2y: {values['twoYearsAgo']:.1f} ({((values['today']-values['twoYearsAgo'])/values['twoYearsAgo'])*100:.1f}%)"

    notification(tweet)
        
else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

# Update save file
savePickle(saveFile, lastDate)