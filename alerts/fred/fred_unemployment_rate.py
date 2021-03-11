#  Unemployment Rate, monthly

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


six_months = datetime.now() + relativedelta(months=+6)

# Load save file
saveFile = 'fred_unemployment_rate.pickle'
lastAvailableDate = loadPickle(saveFile)

# Set dates for CSV
dates = {
    'twoYearsOneMonthAgo': datetime.now() - relativedelta(months=25),
    'twoYearsAgo': datetime.now() - relativedelta(months=24),
    'today': datetime.now()    
}


# Pull data from URL
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE\
&cosd=" + dates['twoYearsOneMonthAgo'].strftime('%Y-%m-%d') + \
"&coed=" + dates['today'].strftime('%Y-%m-%d')
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
    # NO verifyDates needed, as all dates are "monthly day = 1" (Ex: Jan 1, Feb 1)
    values = {
        'twoYearsAgo': getValueFromCSV(csv,dates['twoYearsAgo'].strftime('%Y-%m-%d'),'DATE','UNRATE'),
        'oneYearAgo': getValueFromCSV(csv,dates['oneYearAgo'].strftime('%Y-%m-%d'),'DATE','UNRATE'),
        'sixMonthsAgo': getValueFromCSV(csv,dates['sixMonthsAgo'].strftime('%Y-%m-%d'),'DATE','UNRATE'),
        'threeMonthsAgo': getValueFromCSV(csv,dates['threeMonthsAgo'].strftime('%Y-%m-%d'),'DATE','UNRATE'),
        'oneMonthAgo': getValueFromCSV(csv,dates['oneMonthAgo'].strftime('%Y-%m-%d'),'DATE','UNRATE'),
        #'twoWeeksAgo': getValueFromCSV(csv,dates['twoWeeksAgo'].strftime('%Y-%m-%d'),'DATE','UNRATE'),
        #'oneWeekAgo': getValueFromCSV(csv,dates['oneWeekAgo'].strftime('%Y-%m-%d'),'DATE','UNRATE'),
        #'yesterday': getValueFromCSV(csv,dates['yesterday'].strftime('%Y-%m-%d'),'DATE','UNRATE'),
        'today': getValueFromCSV(csv,dates['today'].strftime('%Y-%m-%d'),'DATE','UNRATE'),
    }

    # Send tweet
    tweet = f"US Unemployment Rate - {lastDate.strftime('%Y-%m-%d')}: {values['today']}%\n\
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