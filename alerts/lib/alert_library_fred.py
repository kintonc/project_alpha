import pandas as pd
from datetime import datetime, timedelta
from alert_library import isfloat

def getValueFromCSV(csv,datetimeStr,dateKey,valueKey):
    return float(csv.loc[csv[dateKey] == datetimeStr,valueKey].values[0])

def verifyDates(csv,dates,dateKey,valueKey):
    for key in dates:
        if dates[key].isoweekday() == 6:
            dates[key] += timedelta(days=2)
        elif dates[key].isoweekday() == 7:
            dates[key] += timedelta(days=1)
        while True:
            if isfloat(csv.loc[csv[dateKey] == dates[key].strftime('%Y-%m-%d'),valueKey].values[0]) == False:
                dates[key] = dates[key] + timedelta(days=1)
            else:
                break
    return dates