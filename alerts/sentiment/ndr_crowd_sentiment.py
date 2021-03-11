import re, sys, os, csv, requests
from datetime import datetime
from bs4 import BeautifulSoup
# Allow /lib folder contents to be imported
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from notification_twitter import notification
from alert_library import loadPickle, savePickle


# Load save file
saveFile = 'ndr_crowd_sentiment.pickle'
lastAvailableDate = loadPickle(saveFile)

# Load page
page = requests.get('https://www.ndr.com/invest/infopage/S574')
soup = BeautifulSoup(page.content, 'html.parser')
data = soup.find_all('span', class_='fixed-width')[0].get_text()

# Get dates and sentiments data
date_of_sentiments = re.findall('[0-9]{2}/[0-9]{2}/[0-9]{4}', data)
date_of_sentiments = [datetime.strptime(x, "%m/%d/%Y") for x in date_of_sentiments]

sentiment_data_row = data.split('NDR Crowd Sentiment',1)[1]
sentiments = re.findall('[0-9]{2}.[0-9]{3}',sentiment_data_row)
sentiments = [float(x) for x in sentiments]
sentimentAvg = sum(sentiments) / len(sentiments)

#print(date_of_sentiments) For debugging
#print(sentiments)

if lastAvailableDate < max(date_of_sentiments):
    tweet = f"NDR Crowd Sentiment - {max(date_of_sentiments).strftime('%Y-%m-%d')}\n\
    5-day MA: {sentimentAvg:.3f}\n\n"

    # Add data from each day to twee
    max_length = max(len(date_of_sentiments),len(sentiments))

    for i in range(max_length):
        tweet += f"{date_of_sentiments[i]}: {sentiments[i]:.3f}\n"

    notification(tweet)

    with open('ndr_crowd_sentiment.csv','w') as f:
        writer = csv.writer(f)

        if os.path.isfile('ndr_crowd_sentiment.csv'):
            writer.writerow(['date', 'sentiment'])

        for i in range(max_length-1, -1, -1):
            writer.writerow([date_of_sentiments[i], sentiments[i]])

    savePickle(saveFile, max(date_of_sentiments))

else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))


