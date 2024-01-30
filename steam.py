#!/usr/bin/env python3

from bs4 import BeautifulSoup
import datetime
import json
import os
import re
import requests
from fuzzywuzzy import fuzz

# Base GOG URL
STEAM_URL = "https://store.steampowered.com/app/"
STEAM_DETAILS_URL = "https://store.steampowered.com/api/appdetails"

# Where search queries are sent
SEARCH_URL = "http://api.steampowered.com/ISteamApps/GetAppList/v2/"

# Suffix added to all search queries
SEARCH_SUFFIX = ""

# Search results are tagged with this string under the 'seleniumId' tag
GAME_HTML_ELEMENT = "productTile"

cookies = { 'birthtime': '470682001', 'lastagecheck' : '1-0-1985', 'mature_content': '1' }

# Media folder names as used by EmulationStation
# and their availability from within GOG.com
# ==============================================
# 3dboxes			- No
# backcovers		- No
# covers			- No
# fanart			- No
# marquees			- Yes
# miximages			- No
# physicalmedia		- No
# screenshots		- Yes
# titlescreens
# videos			- Yes; linked Youtube clips

# Metadata entries
# Name				- Yes
# Description		- Yes
# Rating
# Release Date (YYYY-MM-DD)
# Developer			- Yes
# Publisher			- Yes
# Genre
# Players
# Controller

MEDIA = {
	'3dboxes' : False,
	'cover' : True,
	'data' : True,
	'marquee' : True,
	'miximages' : False,
	'screens' : True,
	'physical' : False,
	'video' : True,
	'title' : True
}

class Steam():
	
	def __init__(self, debug = False):
		self.data_block = None
		self.debug = debug
		self.apps_ids = False
		
		# Get steam app id's list
		try:
			print("")
			print("Retriving Steam App entries from steampowered.com")
			r = requests.get(SEARCH_URL, cookies = cookies)
			if (r.status_code != 200):
				print("- Skipped, no data returned %s" % (r.status_code))
			else:
				app_ids = json.loads(r.text)
				print("- Found [%d]" % len(app_ids['applist']['apps']))
				self.app_ids = app_ids['applist']['apps']
					
		except Exception as e:
			print("- Error making HTTP search request to %s" % SEARCH_URL)
			print(e)
			return False
	
	def get_search(self, name = ""):
		""" Get the app_ids list for a given game name """
		
		search_results = []
		try:
			if self.app_ids:
				print("")
				print("Searching %s local Steam Apps for %s:" % (len(self.app_ids), name))
				for app in self.app_ids:
					if name.upper() in app['name'].upper():
						search_results.append(app)
					else:
						r = fuzz.token_sort_ratio(name, app['name'])
						if r > 75:
							search_results.append(app)
					
				print("- Found [%d]" % len(search_results))
		except Exception as e:
			print("- Error searching AppID's")
			print(e)
			
		return search_results
	
	def get_game(self, game = None, game_url = None):
		""" Get a single Steam data object for a game """
		
		html = False
		
		try:
			app_id = str(game['provider_id'])
			print("")
			print("Retrieving game data from Steam for %s:" % game['provider_id'])
			game_url = STEAM_DETAILS_URL + "?appids=" + app_id
			r = requests.get(game_url, cookies=cookies)
			if (r.status_code != 200):
				print("- Skipped %s, query returned %s" % (game_url, r.status_code))
			else:
				html = r.text
				print("- Returned %s bytes" % len(html))
				game_data = json.loads(html)
				if str(app_id) in game_data.keys():
					if 'success' in game_data[str(app_id)].keys():
						if game_data[str(app_id)]['success'] is True:
							self.data_block = game_data[str(app_id)]['data']
							return self.data_block			
		except Exception as e:
			print("- Error make HTTP game request to %s" % game_url)
			print(e)
			return False
			
		return html
	
	def get_data(self, game_url = "", text = ""):
		""" This is a no-op for steam data """
		return self.data_block
	
	def get_href_from_fragment(self, app = None, url_type = None):
		""" Return an href value from a given HTML fragment """
			
		if url_type is None:
			return str(app['appid'])
		if url_type == "game":
			return STEAM_URL + str(app['appid'])
		if url_type == "data":
			return STEAM_DETAILS_URL + "?appids=" + str(app['appid'])
		
		
	def get_gamename_from_fragment(self, app = None):
		""" Return game title from given HTML fragment """
	
		return app['name']
		
	def get_description_from_fragment(self, text = None):
		""" Return game description from given api data """
		desc = None
	
		try:
			if 'detailed_description' in text.keys():
				soup = BeautifulSoup(text['detailed_description'])
				return soup.get_text()
				print("- Found description")
		except Exception as e:
			print("- Unable to extract game description from fragment")
			print(e)
			
		return desc
		
	def get_developer_from_fragment(self, text = ""):
		developer = None
	
		try:
			if 'developers' in text.keys():
				developer = ", ".join(text['developers'])
				print("- Found developer [%s]" % developer)
				
		except Exception as e:
			print("- Unable to extract game developer from fragment")
			print(e)
			
		return developer
	
	def get_publisher_from_fragment(self, text = ""):
		publisher = None
	
		try:
			if 'publishers' in text.keys():
				publisher = ", ".join(text['publishers'])
				print("- Found publisher [%s]" % publisher)
		except Exception as e:
			print("- Unable to extract game publisher from fragment")
			print(e)
			
		return publisher
	
	def get_genre_from_fragment(self, text = ""):	
		genre = None
	
		try:
			if 'genres' in text.keys():
				if len(text['genres']) > 0:
					genre = text['genres'][0]['description']
					print("- Found genre [%s]" % genre)
		except Exception as e:
			print("- Unable to extract game genre from fragment")
			print(e)
			
		return genre
	
	def get_rating_from_fragment(self, text = ""):
		rating = 0
		
		try:
			if 'metacritic' in text.keys():
				rating = text['metacritic']['score'] / 100
				print("- Found rating [%s]" % rating)
		except Exception as e:
			print("- Unable to extract game rating from fragment")
			print(e)
			
		return rating
	
	def get_date_from_fragment(self, text = ""):
		""" Steam has dates in DD MON, YYYY format... which is a pain. """
		release_date = ""
		
		try:
			if 'release_date' in text.keys():
				release_date = text['release_date']['date']
				release_date = datetime.datetime.strptime(release_date, '%d %b, %Y')
				release_date = release_date.strftime('%Y%m%d') + "T000000"
				print("- Found release date [%s]" % release_date)
		except Exception as e:
			print("- Unable to extract game release date from fragment")
			print(e)
			
		return release_date
	
	def get_players_from_fragment(self, text = ""):
		
		return 1
	
	def get_title_from_fragment(self, text = ""):
		""" Return game title """
		name = None
	
		if self.data_block:
			name = self.data_block['name']
			print("- Found title %s" % name)
			return name
		else:
			print("- Title extraction is only possible if we have extracted the API data!")
			return False
	
	def get_cover(self):
		""" Extract game cover art """
		
		# Uses the 'header' image
		
		if self.data_block:
			if 'header_image' in self.data_block.keys():
				print("- Found cover: %s" % self.data_block['header_image'])
				return self.data_block['header_image']
				
		else:
			print("- Art extraction is only possible if we have extracted the API data!")
			return False
			
	def get_marquee(self):
		""" Extract game marquee/transparent game logo/title """
		
		# Uses the 'capsule' image
		
		if self.data_block:
			if 'capsule_image' in self.data_block.keys():
				print("- Found marquee: %s" % self.data_block['capsule_image'])
				return self.data_block['capsule_image']
		else:
			print("- Art extraction is only possible if we have extracted the API data!")
			return False
		
	def get_title(self):
		""" Extract game titlescreen """
		
		return False
		
	def get_screen(self):
		""" Extract screenshots """
		
		screenshots = []
		
		if self.data_block:
			if 'screenshots' in self.data_block.keys():
				for s in self.data_block['screenshots']:
					shot = s['path_full']
					print("- Found screenshot: %s" % shot)
					screenshots.append(shot)
			if len(screenshots) > 0:
				return screenshots[0]
		else:
			print("- Art extraction is only possible if we have extracted the API data!")
			return False
				
		return False
			
	def get_video(self):
		""" Extract videos """
		
		videos = []
		
		if self.data_block:
			if 'movies' in self.data_block.keys():
				for v in self.data_block['movies']:
					print("- Found video %s" % (v['mp4']['480']))
					videos.append(v['mp4']['480'])
		else:
			print("- Art extraction is only possible if we have extracted the API data!")
			return False
	
		if len(videos) > 0:
			return videos[0]
		
	def download_video(self, game = None, download_path = "", art_type = "video", enable_overwrite = False):
		""" Download a video """
		
		try:
			print("- Downloading stream")
			path = os.path.join(download_path, "videos")
			filename = game['filename'] + ".mp4"
			if (os.path.isfile(os.path.join(path, filename))) and (enable_overwrite is False):
				print("- ... already exists, skipping (Hint: -f to overwrite)")
				return False
			else:
				r = requests.get(game[art_type], stream=True)
				if (r.status_code == 200):
					path = os.path.join(download_path, "videos")
					f = open(path + "/" + filename, "wb")
					for chunk in r.iter_content(chunk_size=128):
						f.write(chunk)
					f.close()
					print("- ... downloaded %s" % (path + "/" + filename))
					return True
				
		except Exception as e:
			print("- Error attempting to download %s" % (game['video']))
			print(e)