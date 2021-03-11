# Economy Now - GDP Nowcasting

# Import default libs
import requests, sys, os, re, csv
from datetime import datetime
from bs4 import BeautifulSoup
# Import custom libs
# Allow /lib folder contents to be imported
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from notification_twitter import notification
from alert_library import loadPickle, savePickle

# Load save file
saveFile = 'economynow.pickle'
lastAvailableDate = loadPickle(saveFile)

# Load webpage to be scraped
page = requests.get('https://www.frbatlanta.org/cqer/research/gdpnow')
soup = BeautifulSoup(page.content, 'html.parser')

# Pull GDP growth estimate and date
estimate = soup.select('h3#Slot')[0].get_text()

estimate = estimate.replace('\r','')
estimate = estimate.replace('\n','')

growth_estimate = re.findall('-?[0-9]+.[0-9]', estimate)[0]
date_of_estimate_str = re.findall('—.*', estimate)[0]
date_of_estimate_str = date_of_estimate_str.replace('—','')

# Check if this estimate is newer than last available estimate
# If so, post on Twitter and update CSV
date_of_estimate = datetime.strptime(date_of_estimate_str, '%B %d, %Y')

if lastAvailableDate < date_of_estimate:
    tweet = f"US GDP Economy Now - {date_of_estimate_str}\n\
    Next qtr: {growth_estimate}%"

    notification(tweet)

    if os.path.isfile('economynow.csv'):
        with open('economynow.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([date_of_estimate, growth_estimate])
    else:
        with open('economynow.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["date","growth_estimate"])
            writer.writerow([date_of_estimate,growth_estimate])

    # Update save file with latest estimate date
    savePickle(saveFile, date_of_estimate)

else:
    print('Not updated, no new data, last available data is ' + lastAvailableDate.strftime('%Y-%m-%d %H:%M:%S'))

