import sys
sys.path.insert(1, '/home/pi/dev/stocks')

from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
import datetime, re, scp, time

# parameters
url = "https://www.stocktwits.com/"


# set chrome options
options = webdriver.ChromeOptions();

options.add_argument("--headless")  
options.add_argument('--user-data-dir=/home/pi/.config/chromium')
#options.add_argument("--no-sandbox")
#options.add_argument("--disable-dev-shm-usage")


# open chrome webdriver, go to a website, and get results
wd = webdriver.Chrome('chromedriver',options=options)
print(url)
wd.get(url)
time.sleep(10) # sleep for 10 seconds to ensure page has loaded
content1 = wd.page_source
soup1 = BeautifulSoup(content1, 'html5lib')


# We want to use XPath to scrape elements
dom = etree.HTML(str(soup1)) # convert HTML to XPath

# Xpath code
xpathCode = '//div[@id=\'global-header\']/div[contains(@class,\'st_DmhifDD\')]/div[contains(@class,\'st_cvvdt6g\')]/div[contains(@class,\'lib_iAc2fkL\')]'

# Match based on XPATH. 
matchedElementsAsBytesList = [] # create empty lists to store all XPath elements. Note that XPath elements are stored as bytes.

for elem in dom.xpath(xpathCode): # for every element in XPath, store it in a list
    matchedElementsAsBytesList.append(etree.tostring(elem))

# combine all elements into one variable
matchedElementsAsBytes = b''.join(matchedElementsAsBytesList) 

# convert bytes to string
elementAsStr = str(matchedElementsAsBytes)

# only match the <span classes> (which have the actual stock tickers we are looking for)
searchResults_ticker = re.findall('<span class="lib_1SXg-su lib_2WawZPB">(.{1,5})<\/span>', elementAsStr)
searchResults_percentage = re.findall('<span class="lib_2H63hKL lib_2WawZPB (.{1,100})">(.{1,10}%)<\/span>', elementAsStr)

# Debugging statements
#print(searchResults_ticker)
#print(searchResults_percentage)

wd.close()

# =============================
# =============================
# create HTML page
# =============================
# =============================


greenDiv = 'lib_3ftZEIu'
redDiv = 'lib_hYxgIpE'

f = open('/home/pi/dev/stocks/project_alpha/monitor/stocktwits.html','w')

message = """<html>
<head>
<style>
table, tbody, th, td {
  border: 1px solid black;
  border-collapse: collapse;
  background-color: #fff;
  padding: 5px;
}
body {
  font-family:Arial;
}
</style>

<body>
<p style="font-size: 1.5em;">Stocktwits</p>
<p style="font-size: 1em;">""" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p><br>
<table>
<tbody>"""

for i in range(0,10):
    message += """<tr>
    <td>"""
    message += searchResults_ticker[i]
    message += """</td>
                <td style="color:"""
    
    if searchResults_percentage[i][0].find(greenDiv) != -1:
        message += """#277625;">""" # green text
    else:
        message += """#DB2413;">""" # red text
        
    message += searchResults_percentage[i][1] + "</td></tr>"

message += """</tbody>
</table>
</body>
</html>"""

f.write(message)
f.close()

scp.scpToServer('/home/pi/dev/project_alpha/monitor/stocktwits.html', '/home/kintonme/public_html/stock')