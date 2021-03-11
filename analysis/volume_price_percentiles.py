from math import sqrt
import yfinance as yf 
import datetime
import pandas as pd
import os
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

def align_yaxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    inv = ax2.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
    miny, maxy = ax2.get_ylim()
    ax2.set_ylim(miny+dy, maxy+dy)

def volume_price_percentiles(ticker,period):
    output = []
    output.append(ticker)
    output.append(period)

    contract=yf.Ticker(ticker)
    df = contract.history(period=period) 
    
    
    for i in range(0,df.shape[0]-1):
        df.loc[df.index[i+1],'changepct'] = ((df['Close'].iloc[i+1] - df['Close'].iloc[i]) / 
                                              df['Close'].iloc[i])

    df = df.reset_index()
    print(df)
    
    df['changepctMA'] = df['changepct'].rolling(window=5).mean()
     
    # Find order of magnitude of 5th percentile volume, normalize by this
    df['volumeNormalized'] = df['Volume'] / df['Volume'].quantile(0.5)
    df['volumeNormalizedMA'] = df['volumeNormalized'].rolling(window=5).mean()

    #low_vol_order_of_magnitude = math.floor(math.log(df['Volume'].quantile(0.5), 10))
    #df['volumeNormalized'] = df['Volume'] / (10**low_vol_order_of_magnitude)
    
    #print(df)
    #print('\n')  
    
    output.append("Volume percentiles:")    
    print(df['changepctMA'].iloc[-1])
    output.append(f"Today: {df['volumeNormalized'].iloc[-1]:.2f}")  
    output.append(f"99%: {df['volumeNormalized'].quantile(0.99):.2f}")  
    output.append(f"95%: {df['volumeNormalized'].quantile(0.95):.2f}")  
    output.append(f"90%: {df['volumeNormalized'].quantile(0.90):.2f}")  
    output.append(f"75%: {df['volumeNormalized'].quantile(0.75):.2f}")  
    output.append(f"50%: {df['volumeNormalized'].quantile(0.50):.2f}")  
    output.append(f"25%: {df['volumeNormalized'].quantile(0.25):.2f}")  
    output.append(f"10%: {df['volumeNormalized'].quantile(0.10):.2f}")  
    output.append(f"5%: {df['volumeNormalized'].quantile(0.05):.2f}")  
    output.append(f"1%: {df['volumeNormalized'].quantile(0.01):.2f}")  
    output.append('')
    output.append('')

    output.append("Percent Change percentiles:")    
    output.append(f"Today: {df['changepct'].iloc[-1]*100:.2f}%")  
    output.append(f"99%: {df['changepct'].quantile(0.99)*100:.2f}%") 
    output.append(f"95%: {df['changepct'].quantile(0.95)*100:.2f}%") 
    output.append(f"90%: {df['changepct'].quantile(0.90)*100:.2f}%") 
    output.append(f"75%: {df['changepct'].quantile(0.75)*100:.2f}%") 
    output.append(f"50%: {df['changepct'].quantile(0.50)*100:.2f}%") 
    output.append(f"25%: {df['changepct'].quantile(0.25)*100:.2f}%") 
    output.append(f"10%: {df['changepct'].quantile(0.10)*100:.2f}%") 
    output.append(f"5%: {df['changepct'].quantile(0.05)*100:.2f}%") 
    output.append(f"1%: {df['changepct'].quantile(0.01)*100:.2f}%") 

    
    # create figure and axis objects with subplots()
    fig,ax = plt.subplots()
    # make a plot
    ax.plot(df['Date'], df['changepctMA'], color="blue", marker="")
    # set x-axis label
    ax.set_xlabel("Date",fontsize=14)
    # set y-axis label
    ax.set_ylabel("changepctMA",color="blue",fontsize=14)
    # format date axis
    date_form = DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(date_form)

    # Ensure a major tick for each week using (interval=1) 
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    
    # twin object for two different y-axis on the sample plot
    ax2=ax.twinx()
    ax2.xaxis.set_major_formatter(date_form)
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

    # make a plot with different y-axis using second axis object
    ax2.plot(df['Date'], df['volumeNormalized'],color="green",marker="")
    ax2.set_ylabel("volumeNormalized",color="green",fontsize=14)
    plt.title(ticker,fontsize=20)
    plt.grid(True)
    #ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax.get_yticks())))
    #plt.show()    


    '''plt.figure(figsize=[15,10])
    plt.grid(True)
    plt.plot(df['volumeNormalizedMA'],label='volumeNormalizedMA')
    plt.plot(df['changepctMA'],label='changePctMA')
    plt.legend(loc=2)'''


    return output