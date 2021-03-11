import datetime
import tweepy
import api_keys

def notification(message):
	consumer_key = api_keys.twitter_consumer_key
	consumer_secret = api_keys.twitter_consumer_secret
	access_token = api_keys.twitter_access_token
	access_token_secret = api_keys.twitter_access_token_secret

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth)

	datetimenowstr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	message += ('\n' + datetimenowstr)

	try:
		if api.update_status(message):
			print('POSTed to Twitter: %s' % message)
	except tweepy.error.TweepError as e:
		print(e)			