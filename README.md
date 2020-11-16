# financial_alerts

A collection of Python scripts that monitors:

1. [FRED (Federal Reserve Economic Data) stats](https://fred.stlouisfed.org/)
2. Sentiment data
    * [Smart Money confidence](https://sentimentrader.com/smart-money/)
    * [NDR Crowd Sentiment](https://www.ndr.com/invest/infopage/S574)
    * [Fear and Greed index](https://money.cnn.com/data/fear-and-greed/)
    * [AAII Investor Sentiment Survey](https://www.aaii.com/sentimentsurvey?)
3. [EconomyNow GDPNow Nowcasting, for latest GDP projections](https://www.frbatlanta.org/cqer/research/gdpnow)
4. Alternative data, to gauge economic activity, such as...
    * [CASS Freight Index](https://www.cassinfo.com/freight-audit-payment/cass-transportation-indexes/cass-freight-index)
5. Stock technical indicator alerts
    * Put/call ratios for various stocks
    * RSI alerts (if stock goes below RSI < 30, for example)

### Library Dependencies (make sure you have these libraries installed before running scripts):
1. Pickle
2. Pandas / Numpy
3. JSON
4. Requests
5. URLLib
6. Tweepy
7. Selenium Webdriver
8. BeautifulSoup
9. LXML
