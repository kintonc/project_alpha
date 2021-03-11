# No longer use IFTTT to generate stonk alerts, as of 2020/11/01
# Now, we use Twitter

import datetime
import requests
from api_keys import ifttt_api_keys

def notification(message):
	
	datetimenowstr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	message += ('\n' + datetimenowstr)
	requests.post("https://maker.ifttt.com/trigger/rsi_alert/with/key" + ifttt_api_keys,
					json={'value1': message})
	print('POSTed to IFTTT: %s' % message)