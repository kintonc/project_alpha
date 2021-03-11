#  Consumer Price Index for All Urban Consumers, monthly

# Import default libs
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import sys, os
# Import custom libs
# Allow /lib folder contents to be imported
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from notification_twitter import notification
from alert_library import loadPickle, savePickle
from alert_library_fred import getValueFromCSV, verifyDates


# Load save file
saveFile = 'fred_cpi_urban.pickle'
lastAvailableDate = loadPickle(saveFile)

# Set dates for CSV
dates = {
    'twoYearsSixMonthAgo': datetime.now() - relativedelta(months=30), # we set CSV start date to be 2.5 years ago, as we may need to pull values from 25/26/27 mths ago
    'twoYearsAgo': datetime.now() - relativedelta(months=24),
    'today': datetime.now()    
}

# Pull data from URL
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL\
&cosd=" + dates['twoYearsSixMonthAgo'].strftime('%Y-%m-%d') + \
"&coed=" + dates['today'].strftime('%Y-%m-%d')
print(url)
csv = pd.read_csv(url)
print(csv)

# get date of last datapoint, in CSV file
lastDate = datetime.strptime(csv['DATE'].iloc[-1],'%Y-%m-%d')

# If we have a new update:
if lastAvailableDate < lastDate:
    # Pull rate from 2 yrs ago, 1 yr ago, etc
    dates['twoYearsAgo'] = (lastDate - relativedelta(months=24)).date()
    dates['oneYearAgo'] = (lastDate - relativedelta(months=12)).date()
    dates['sixMonthsAgo'] = (lastDate - relativedelta(months=6)).date()
    dates['threeMonthsAgo'] = (lastDate - relativedelta(months=3)).date()
    dates['oneMonthAgo'] = (lastDate - relativedelta(months=1)).date()
    dates['today'] = lastDate.date() # update today to the date of the last unemployment data point (ex: 02/01/2021)
    # NO Verify needed, as these values are monthly (always on day = 1, ex: Jan 1, Feb 1, etc)
    values = {
        'twoYearsAgo': getValueFromCSV(csv,dates['twoYearsAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
        'oneYearAgo': getValueFromCSV(csv,dates['oneYearAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
        'sixMonthsAgo': getValueFromCSV(csv,dates['sixMonthsAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
        'threeMonthsAgo': getValueFromCSV(csv,dates['threeMonthsAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
        'oneMonthAgo': getValueFromCSV(csv,dates['oneMonthAgo'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
        'today': getValueFromCSV(csv,dates['today'].strftime('%Y-%m-%d'),'DATE','CPIAUCSL'),
    }

    # Send tweet
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






