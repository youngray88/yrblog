import json
import requests
from flask import current_app
from hashlib import md5
from random import randint

def translate(text,source_lan='en',dest_lan='zh'):
	print('text:{}-from:{}-to:{}'.format(text,source_lan,dest_lan))
	url = current_app.config['BD_TRANSLATOR_URL']
	appid = current_app.config['BD_TRANSLATOR_APPID']
	salt = randint(1,10000)
	key = current_app.config['BD_TRANSLATOR_KEY']
	sign_data = str(appid) + text + str(salt) + str(key)
	sign = md5(sign_data.encode('utf-8')).hexdigest()
	res = requests.get('{}?q={}&from={}&to={}&appid={}&salt={}&sign={}'.format(url,text,source_lan,dest_lan,appid,salt,sign))
	if res.status_code != 200:
		return 'Error:translate failed.'
	return res.json()
