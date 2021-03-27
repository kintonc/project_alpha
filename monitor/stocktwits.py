import sys
sys.path.insert(1, '/home/pi/dev/stocks')
from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
import datetime, re, scp, time

# Print time now, for debugging
print('START SCRIPT - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# =============================
# =============================
# 1 - Pull data from Stocktwits
# =============================
# =============================
print('START 1: PULL DATA FROM STOCKTWITS - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

url = "https://www.stocktwits.com/"

# Set Chrome/Chromium options
options = webdriver.ChromeOptions();
options.add_argument("--headless")
options.add_argument('--user-data-dir=/home/pi/.config/chromium')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Open Chrome Webdriver, go to website
wd = webdriver.Chrome('chromedriver',options=options)
print('START 1A: OPEN STOCKTWITS IN CHROME - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
wd.get(url)
print('END 1A: OPEN STOCKTWITS IN CHROME - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
time.sleep(10) # sleep for 10 seconds to ensure page has loaded
print('START 1B: INITIALIZE BEAUTIFULSOUP - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
content = wd.page_source
soup = BeautifulSoup(content, 'html5lib')
print('END 1B: INITIALIZE BEAUTIFULSOUP - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# We want to use XPath to scrape elements
print('START 1C: XPATH SELECTION - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
dom = etree.HTML(str(soup)) # convert HTML to XPath
# Xpath code
xpathCode = '//div[@id=\'global-header\']/div[contains(@class,\'st_DmhifDD\')]/div[contains(@class,\'st_cvvdt6g\')]/div[contains(@class,\'lib_iAc2fkL\')]'

# Match based on XPATH. 
matchedElementsAsBytesList = [] # create empty lists to store all XPath elements. Note that XPath elements are stored as bytes.

# for every element in XPath, store it in a list
for elem in dom.xpath(xpathCode):
    matchedElementsAsBytesList.append(etree.tostring(elem))

# combine all elements into one variable
matchedElementsAsBytes = b''.join(matchedElementsAsBytesList) 

# convert bytes to string
elementAsStr = str(matchedElementsAsBytes)

# only match the <span classes> (which have the actual stock tickers we are looking for)
searchResults_ticker = re.findall('<span class="lib_1SXg-su lib_2WawZPB">(.{1,5})<\/span>', elementAsStr)
searchResults_percentage = re.findall('<span class="lib_2H63hKL lib_2WawZPB (.{1,100})">(.{1,10}%)<\/span>', elementAsStr)

print('END 1C: XPATH SELECTION - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Debugging statements
#print(searchResults_ticker)
#print(searchResults_percentage)

wd.close()
wd.quit()

# =============================
# =============================
# 2 - Create HTML page
# =============================
# =============================
print('START 2: CREATE HTML PAGE - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

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

# Add the stocks into the table
for i in range(0,len(searchResults_ticker)):
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

# =============================
# =============================
# 3 - Send HTML page to server via SCP
# =============================
# =============================
print('START 3: SCP, SEND PAGE TO SERVER - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

scp.scpToServer('/home/pi/dev/project_alpha/monitor/stocktwits.html', '/home/kintonme/public_html/stock')

# END SCRIPT
print('END SCRIPT - ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))