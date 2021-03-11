# ICE BofA US High Yield Index Option-Adjusted Spread vs Treasury - Daily

# Import default libs
import pandas as pd
from datetime import datetime, timedelta
import sys, os
# Import custom libs
# Allow /lib folder contents to be imported
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from notification_twitter import notification
from alert_library import loadPickle, savePickle
from alert_library_fred import getValueFromCSV, verifyDates

# Load save file
saveFile = 'fred_high_yield_bond_spread.pickle'
lastAvailableDate = loadPickle(saveFile)

# Set dates for CSV
dates = {
    'twoYearsOneMonthAgo': datetime.now() - timedelta(days=760),
    'twoYearsAgo': datetime.now() - timedelta(days=730),
    'today': datetime.now()    
}

# Pull data from URL
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLH0A0HYM2\
&cosd=" + dates['twoYearsOneMonthAgo'].strftime('%Y-%m-%d') + \
"&coed=" + dates['today'].strftime('%Y-%m-%d')
csv = pd.read_csv(url)
print(csv)

# get date of last datapoint, in CSV file
lastDate = datetime.strptime(csv['DATE'].iloc[-1],'%Y-%m-%d')



# If we have a new update:
if lastAvailableDate < lastDate:
    # Pull rate from 2 yrs ago, 1 yr ago, etc
    dates['twoYearsAgo'] = (lastDate - timedelta(days=730)).date()
    dates['oneYearAgo'] = (lastDate - timedelta(days=365)).date()
    dates['sixMonthsAgo'] = (lastDate - timedelta(days=182)).date()
    dates['threeMonthsAgo'] = (lastDate - timedelta(days=91)).date()
    dates['oneMonthAgo'] = (lastDate - timedelta(days=30)).date()
    dates['twoWeeksAgo'] = (lastDate - timedelta(days=14)).date()
    dates['oneWeekAgo'] = (lastDate - timedelta(days=7)).date()
    dates['yesterday'] = (lastDate - timedelta(days=1)).date()
    dates['today'] = lastDate.date()
    dates = verifyDates(csv,dates,'DATE','BAMLH0A0HYM2')
    values = {
        'twoYearsAgo': getValueFromCSV(csv,dates['twoYearsAgo'].strftime('%Y-%m-%d'),'DATE','BAMLH0A0HYM2'),
        'oneYearAgo': getValueFromCSV(csv,dates['oneYearAgo'].strftime('%Y-%m-%d'),'DATE','BAMLH0A0HYM2'),
        'sixMonthsAgo': getValueFromCSV(csv,dates['sixMonthsAgo'].strftime('%Y-%m-%d'),'DATE','BAMLH0A0HYM2'),
        'threeMonthsAgo': getValueFromCSV(csv,dates['threeMonthsAgo'].strftime('%Y-%m-%d'),'DATE','BAMLH0A0HYM2'),
        'oneMonthAgo': getValueFromCSV(csv,dates['oneMonthAgo'].strftime('%Y-%m-%d'),'DATE','BAMLH0A0HYM2'),
        'twoWeeksAgo': getValueFromCSV(csv,dates['twoWeeksAgo'].strftime('%Y-%m-%d'),'DATE','BAMLH0A0HYM2'),
        'oneWeekAgo': getValueFromCSV(csv,dates['oneWeekAgo'].strftime('%Y-%m-%d'),'DATE','BAMLH0A0HYM2'),
        'yesterday': getValueFromCSV(csv,dates['yesterday'].strftime('%Y-%m-%d'),'DATE','BAMLH0A0HYM2'),
        'today': getValueFromCSV(csv,dates['today'].strftime('%Y-%m-%d'),'DATE','BAMLH0A0HYM2'),
    }

    # Send tweet
    tweet = f"US BofA High Yield Index Option-Adjusted Spread vs Treasury - {lastDate.strftime('%Y-%m-%d')}: {values['today']:.2f}%\n\
1d: {values['yesterday']:.2f}% ({((values['today']-values['yesterday'])/values['yesterday'])*100:.1f}%)\n\
1w: {values['oneWeekAgo']:.2f}% ({((values['today']-values['oneWeekAgo'])/values['oneWeekAgo'])*100:.1f}%)\n\
2w: {values['twoWeeksAgo']:.2f}% ({((values['today']-values['twoWeeksAgo'])/values['twoWeeksAgo'])*100:.1f}%)\n\
1m: {values['oneMonthAgo']:.2f}% ({((values['today']-values['oneMonthAgo'])/values['oneMonthAgo'])*100:.1f}%)\n\
3m: {values['threeMonthsAgo']:.2f}% ({((values['today']-values['threeMonthsAgo'])/values['threeMonthsAgo'])*100:.1f}%)\n\
6m: {values['sixMonthsAgo']:.2f}% ({((values['today']-values['sixMonthsAgo'])/values['sixMonthsAgo'])*100:.1f}%)\n\
1y: {values['oneYearAgo']:.2f}% ({((values['today']-values['oneYearAgo'])/values['oneYearAgo'])*100:.1f}%)\n\
2y: {values['twoYearsAgo']:.2f}% ({((values['today']-values['twoYearsAgo'])/values['twoYearsAgo'])*100:.1f}%)"

    notification(tweet)
        
else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

# Update save file
savePickle(saveFile, lastDate)