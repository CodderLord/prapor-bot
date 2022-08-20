import requests
from lists_conf import USER_AGENT
import time


def get_soup(urls):
	try:
		req = requests.get(urls, headers=USER_AGENT)
		return req
	except Exception as err:
		print(f"{err=}")
		
		