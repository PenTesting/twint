from . import datelock, db, get, feed, output
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import concurrent.futures
import datetime
import re
import sys

class User:

	def __init__(self, config):
		self.config = config
		self.init = -1
		
		if self.config.Elasticsearch:
			print("Indexing to Elasticsearch @ " + str(self.config.Elasticsearch))

		if self.config.Database:
			print("Inserting into Database: " + str(self.config.Database))
			self.conn = db.init(self.config.Database)
			if isinstance(self.conn, str):
				print(str)
				sys.exit(1)
		else:
			self.conn = ""

		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.main())

	async def Profile(self):
		connect = aiohttp.TCPConnector(verify_ssl=False)
		async with aiohttp.ClientSession(connector=connect) as session:
			response = await get.Response(session, await get.Url(self.config, self.init).profile())
		self.profile = {}
		try:
			self.profile = self.Info(response)
		except:
			pass

	def Info(self, response):
		soup = BeautifulSoup(response, "html.parser")
		name = "".join(soup.select(".ProfileHeaderCard-nameLink")[0].stripped_strings)
		screen_name = "".join(soup.select(".ProfileHeaderCard-screenname")[0].stripped_strings)
		bio = "".join(soup.select(".ProfileHeaderCard-bio")[0].strings)
		location = "".join(soup.select(".ProfileHeaderCard-location")[0].stripped_strings)
		url = "".join(soup.select(".ProfileHeaderCard-url")[0].stripped_strings)
		joinDate = "".join(soup.select(".ProfileHeaderCard-joinDate")[0].stripped_strings)
		tweets = "".join(soup.select("[data-nav='tweets'] > [data-count]")[0]['data-count'])
		following = "".join(soup.select("[data-nav='following'] > [data-count]")[0]['data-count'])
		followers = "".join(soup.select("[data-nav='followers'] > [data-count]")[0]['data-count'])
		favorites = "".join(soup.select("[data-nav='favorites'] > [data-count]")[0]['data-count'])
		profile = {
			"name":name,
			"screen_name":screen_name,
			"bio":bio,
			"location":location,
			"url":url,
			"joinDate":joinDate,
			"tweets":int(tweets),
			"following":int(following),
			"followers":int(followers),
			"likes":int(favorites)
		}
		print(profile)
		return profile

	async def main(self):
		if self.config.User_id is not None:
			self.config.Username = await get.Username(self.config.User_id)
		await self.Profile()
