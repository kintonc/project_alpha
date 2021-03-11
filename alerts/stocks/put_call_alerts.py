from math import sqrt
import yfinance as yf
import datetime, os, pickle, sys
import pandas as pd
# Allow /lib folder contents to be imported
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from notification_twitter import notification


tickers = ['AAPL',
          'GOOG']

putCallRatioHigh = 0.7
putCallRatioLow = 0.5

impliedMoveThresholds = {
    '7':0.05,
    '30':0.10,
}

today = datetime.datetime.now().date()

impliedMove = pd.DataFrame(columns=['expiry','daysToExpiry','callsIV','putsIV',
                                    'callsImpliedMove','putsImpliedMove',
                                   'callVolume','putVolume','putCallRatio'])
saveFile = 'put_call_alerts.pickle'

if(os.path.isfile(saveFile)):
    with open(saveFile, 'rb') as f:
        # You must load and save Pickle objects SEQUENTIALLY (https://stackoverflow.com/questions/34674094/is-there-a-way-to-save-multiple-variables-in-python-pickle)
        putCallRatioAlert = pickle.load(f)
        impliedMoveAlert = pickle.load(f)
else:
    putCallRatioAlert = {}
    impliedMoveAlert = {}
    for ticker in tickers:
        putCallRatioAlert[ticker] = True
        impliedMoveAlert[ticker] = {}
        
        for dayThreshold in impliedMoveThresholds:
            impliedMoveAlert[ticker][dayThreshold] = True
            
for ticker in tickers:
    contract=yf.Ticker(ticker)
    contract.options # get the list of expiry dates
    
    callVolumeAllExpiryDates = 0 # reset variables
    putVolumeAllExpiryDates = 0
    
    print('Processing %s... (option expiries follow)' % ticker)
    
    for counter, expiry in enumerate(contract.options):
        daysToExpiry = ((datetime.datetime.strptime(expiry, '%Y-%m-%d').date()) - today).days
        print(expiry)

        calls = contract.option_chain(expiry).calls
        puts = contract.option_chain(expiry).puts

        callVolume = calls['volume'].sum()
        putVolume = puts['volume'].sum()
        putCallRatio = putVolume / callVolume
        callVolumeAllExpiryDates += callVolume
        putVolumeAllExpiryDates += putVolume

        # Only look at calls/puts with 80th+ percentile in volume
        callsWithHighestVolume = calls[calls.volume >= calls.volume.quantile(.80)]
        putsWithHighestVolume = puts[puts.volume >= puts.volume.quantile(.80)]

        # take weighted average (volume * impliedVolatility) to get overall IV
        callsIV = (callsWithHighestVolume["impliedVolatility"] * callsWithHighestVolume["volume"]).sum() \
                    / callsWithHighestVolume["volume"].sum()
        putsIV = (putsWithHighestVolume["impliedVolatility"] * putsWithHighestVolume["volume"]).sum() \
                    / putsWithHighestVolume["volume"].sum()


        impliedMoveCalls = callsIV * sqrt(daysToExpiry / 365)
        impliedMovePuts = putsIV * sqrt(daysToExpiry / 365)

        impliedMove.loc[counter] = [expiry,daysToExpiry,callsIV,putsIV,
                                    impliedMoveCalls,impliedMovePuts,
                                   callVolume,putVolume,putCallRatio]
        #impliedMove.append([expiry,daysToExpiry,callsIV,putsIV,impliedMoveCalls,impliedMovePuts])

    print(impliedMove)


    # Put/Call Ratio for All Expiries
    putCallRatioAllExpiryDates = putVolumeAllExpiryDates / callVolumeAllExpiryDates
    print('Call volume: %d' % callVolumeAllExpiryDates)
    print('Put volume: %d' % putVolumeAllExpiryDates)
    print('Put/Call Ratio: %.4f' % putCallRatioAllExpiryDates)

    # Send to Twitter
    if putCallRatioAlert[ticker] == True and putCallRatioAllExpiryDates > putCallRatioHigh:
        notification('%s > %.2f PUT/CALL RATIO' % (ticker, putCallRatioHigh))
        putCallRatioAlert[ticker] = False
    elif putCallRatioAlert[ticker] == True and putCallRatioAllExpiryDates < putCallRatioLow:
        notification('%s < %.2f PUT/CALL RATIO' % (ticker, putCallRatioLow))
        putCallRatioAlert[ticker] = False
    elif putCallRatioAlert[ticker] == False and putCallRatioLow < putCallRatioAllExpiryDates and putCallRatioAllExpiryDates > putCallRatioHigh:
        putCallRatioAlert[ticker] = True

    
    # Check if implied moves are greater than threshold.
    for key, val in impliedMoveThresholds.items():
        
        # Get the row index that is the least amount of days away from '7 days away', '30 days away', etc
        # https://stackoverflow.com/questions/30112202/how-do-i-find-the-closest-values-in-a-pandas-series-to-an-input-number
        index = impliedMove.iloc[(impliedMove['daysToExpiry']-int(key)).abs().argsort()[:1]].index
            
        # get average of call implied move and put implied move
        impliedMoveAvgOfCallAndPut = (impliedMove.iloc[index]['callsImpliedMove'] 
                                      + impliedMove.iloc[index]['putsImpliedMove']) / 2
        # extract int result from dataframe
        impliedMoveAvgOfCallAndPut = impliedMoveAvgOfCallAndPut.values[0] 
        
        # Send to Twitter
        if impliedMoveAvgOfCallAndPut >= val and impliedMoveAlert[ticker][key] == True:
            impliedMovePercentage = impliedMoveAvgOfCallAndPut * 100
            percentage = val * 100
            notification('%s %s day implied move greater than %.1f%% (%.1f%%)' % (ticker, key, percentage, 
                                                                              impliedMovePercentage))
            impliedMoveAlert[ticker][key] = False
        elif impliedMoveAlert[ticker][key] == False and impliedMoveAvgOfCallAndPut < val:
            impliedMoveAlert[ticker][key] = True
        
with open(saveFile, 'wb') as f:
    # you must save Pickle objects SEQUENTIALLY
    pickle.dump(putCallRatioAlert, f)
    pickle.dump(impliedMoveAlert, f)

f.close()