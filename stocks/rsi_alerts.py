# RSI MONITORING
# Monitor RSI, send alert when RSI < 40, > 70 (or some other value)
# ========================================
# Imports
import pandas as pd
import numpy as np
from talib import RSI, BBANDS
import datetime 
import requests
import pickle
import os.path
import yfinance as yf
from notification_twitter import notification

# ========================================
# User defined variables
# ========================================
symbols = ['AAPL',
           'MSFT',
           'NVDA',
           'VXX'
         ]
rsiLow = 50
rsiHigh = 70

# ========================================
# Script
# ========================================

saveFile = 'rsi_alerts.pickle'
isMarketHours = False # is it between 09:30 and 16:00?

# triggerAlert: if a RSI notif (ex: RSI < 40) has already triggered in the past, IF RSI has NOT gone above 40 
# since it was triggered, we don't want to trigger notif again
# triggerAlert stores this
if(os.path.isfile(saveFile)):
    with open(saveFile, 'rb') as f:
        triggerAlert = pickle.load(f)
else:
    triggerAlert = {}
    for symbol in symbols:
        triggerAlert[symbol] = True

if datetime.datetime.now().time() >= datetime.time(9,30) \
and datetime.datetime.now().time() <= datetime.time(16,0):
    isMarketHours = True
        
for symbol in symbols:
    contract = yf.Ticker(symbol)

    closing_price_daily = contract.history(period="1mo",interval="1d")["Close"]

    # Future improvement: if we want to monitor intraday price and alert for RSI
    if isMarketHours == True:
        closing_price_today = contract.history(period="1d",interval="15m")["Close"]
        closing_price_daily = closing_price_daily.append(closing_price_today[-1:])
        
    #closing_price_daily = closing_price_daily.apply(lambda x: round(x,2)) 
    #print(closing_price_daily[-14:])

    rsi = RSI(closing_price_daily,timeperiod=14)
    print('%s RSI: %.2f' % (symbol, rsi[-1]))
    
    # if we should trigger an alert and thresholds are met:
    if triggerAlert[symbol] == True and (rsi[-1] <= rsiLow):
        triggerAlert[symbol] = False
        notification('%s < %d RSI [14,1d] (%.2f)' % (symbol, rsiLow, rsi[-1]))
    elif triggerAlert[symbol] == True and (rsi[-1] >= rsiHigh):
        notification('%s > %d RSI [14,1d] (%.2f)' % (symbol, rsiHigh, rsi[-1]))
    elif triggerAlert[symbol] == False and (rsi[-1] > rsiLow) and (rsi[-1] < rsiHigh):
        triggerAlert[symbol] = True
    
with open(saveFile, 'wb') as f:
    pickle.dump(triggerAlert, f)

f.close()
