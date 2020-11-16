import os
from datetime import datetime
import pickle
from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
import requests


def loadPickle(saveFile):
    if(os.path.isfile(saveFile)):
        with open(saveFile, 'rb') as f:
            lastAvailableDate = pickle.load(f)
    else:
        lastAvailableDate = datetime(1900,1,1)
    return lastAvailableDate

# saveFile = str, lastAvailableDate = datetime obj
def savePickle(saveFile, lastAvailableDate):
    with open(saveFile, 'wb') as f:
        pickle.dump(lastAvailableDate, f)
    return

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# pullDOM returns a lxml.etree element (a DOM) that can be traversed using XPATH
def retrieveDOM(url):
    options = webdriver.ChromeOptions();
    options.add_argument("--headless")  
    options.add_argument('--user-data-dir=/home/pi/.config/chromium')

    # open chrome webdriver, go to a website, and get result
    wd = webdriver.Chrome('chromedriver',options=options)
    print(url)
    wd.get(url)
    content1 = wd.page_source
    soup1 = BeautifulSoup(content1,features='lxml')

    # We want to use XPath to scrape elements
    dom = etree.HTML(str(soup1)) # convert HTML to XPath
    wd.quit()

    return dom