#!/usr/bin/env python3

from bs4 import BeautifulSoup as soup
import json
import re
import requests


from pytubewrapper import PTWrapper

# Base GOG URL
GOG_URL = "https://www.gog.com"

# Where search queries are sent
SEARCH_URL = GOG_URL + "/en/games?query="

# Suffix added to all search queries
SEARCH_SUFFIX = "&order=desc:score&hideDLCs=true"

# Search results are tagged with this string under the 'seleniumId' tag
GAME_HTML_ELEMENT = "productTile"

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

class GOG():
	
	def __init__(self, debug = False):
		self.data_block = None
		self.debug = debug
	
	def get_search(self, name = ""):
		""" Get the GOG.com search page results for a given game name """
		
		search_results = []
		search_url = SEARCH_URL + name + SEARCH_SUFFIX
		try:
			print("")
			print("Searching GOG.com for %s:" % name)
			r = requests.get(search_url)
			if (r.status_code != 200):
				print("- Skipped %g, query returned %s" % (name, r.status_code))
			else:
				page = soup(r.text, 'html.parser')
				search_results = page.find_all('a', 'product-tile')
				print("- Found [%d]" % len(search_results))
					
		except Exception as e:
			print("- Error making HTTP search request to %s" % search_url)
			print(e)
			
		return search_results
	
	def get_game(self, game = None, game_url = ""):
		""" Get a single GOG.com game page """
		
		html = ""
		
		try:
			print("")
			print("Retrieving game data from GOG.com for %s:" % game_url)
			r = requests.get(game_url)
			if (r.status_code != 200):
				print("- Skipped %s, query returned %s" % (game_url, r.status_code))
			else:
				html = r.text
				print("- Returned %s bytes" % len(html))
			
		except Exception as e:
			print("- Error make HTTP game request to %s" % game_url)
			print(e)
			return False
			
		return html
	
	def get_data(self, game_url = "", text = ""):
		""" Retrieve the embedded json data block within the HTML page """
		card_json = False
		
		try:
			fragment_results = re.findall("cardProduct: {.*", text)
			for f in fragment_results:
				data = f.split("cardProduct: ")
				# Get the dict part
				data = data[1]
				# Trim the trailing javascript ','
				data = data[0:-1]
				# Covnert to python dict
				data = json.loads(data)
				card_json = True
				self.data_block = data
				if self.debug:
					print("- Dumping GOG.com embedded json data:")
					print("---")
					print(self.data_block)
					print("---")
				print("- Extracted GOG.com embedded json data")
		except Exception as e:
			print("- Error getting extended GOG json datablock in HTML")
			print(e)
			
		return card_json
	
	def get_href_from_fragment(self, text = "", url_type = None):
		""" Return an href value from a given HTML fragment """
		href = None
	
		try:
			fragment = soup("%s" % text, 'html.parser')
			tag = fragment.a
			if 'href' in tag.attrs:
				href = tag['href']
		except Exception as e:
			print("- Unable to extract href tag from fragment")
			print(e)
	
		return href
		
	def get_gamename_from_fragment(self, text = ""):
		""" Return game title from given HTML fragment """
		name = None
	
		try:
			fragment = soup("%s" % text, 'html.parser')
			fragment_results = fragment.find_all('div', 'product-tile__title')
			if len(fragment_results) == 1:
				title_fragment = soup("%s" % fragment_results[0], 'html.parser')
				tag = title_fragment.div
				if 'title' in tag.attrs:
					name = tag['title']
		except Exception as e:
			print("- Unable to extract game title from fragment")
			print(e)
			
		return name
		
	def get_description_from_fragment(self, text = ""):
		""" Return game description from given HTML fragment """
		# <div class="description">blah blah blah</div>
		
		desc = None
	
		try:
			fragment = soup("%s" % text, 'html.parser')
			fragment_results = fragment.find_all('div', 'description')
			for f in fragment_results:
				desc_fragment = soup("%s" % f, 'html.parser')
				tag = desc_fragment.div
				# Strip leading and trailing text from the entire description
				desc = tag.get_text().strip()
				print("- Found description (regex)")
				return desc
		except Exception as e:
			print("- Unable to extract game description from fragment")
			print(e)
			
		return desc
		
	def get_developer_from_fragment(self, text = ""):
		
		#<a href="/games?developers=heart-machine"
		#                class="details__link"
		#                gog-track-event="{eventAction: 'click', eventCategory: 'productPageGameDetails', eventLabel: 'Developer: Heart Machine'}"
		#            >Heart Machine</a>
		
		developer = None
	
		try:
			fragment = soup("%s" % text, 'html.parser')
			fragment_results = fragment.find_all(href=re.compile("^/games\?developers\="))
			for f in fragment_results:
				developer = f.text
				print("- Found developer [%s]" % developer)
				return developer
		except Exception as e:
			print("- Unable to extract game developer from fragment")
			print(e)
			
		return developer
	
	def get_publisher_from_fragment(self, text = ""):
		
		#<a href="/games?publishers=heart-machine"
		#                class="details__link"
		#                gog-track-event="{eventAction: 'click', eventCategory: 'productPageGameDetails', eventLabel: 'Publisher: Heart Machine'}"
		#            >Heart Machine</a>
		
		publisher = None
	
		try:
			fragment = soup("%s" % text, 'html.parser')
			fragment_results = fragment.find_all(href=re.compile("^/games\?publishers\="))
			for f in fragment_results:
				publisher = f.text
				print("- Found publisher [%s]" % publisher)
				return publisher
		except Exception as e:
			print("- Unable to extract game publisher from fragment")
			print(e)
			
		return publisher
	
	def get_genre_from_fragment(self, text = ""):
		
		genre = None
	
		try:
			# Genre is in a javascript label and needs to be split out:
			#
			# <a href="/games/action" 
			#                class="details__link"
			#                gog-track-event="{eventAction: 'click', eventCategory: 'productPageGameDetails', eventLabel: 'CAT: Action'}">
			# Action</a>
			#
			fragment_results = re.findall("eventLabel: 'CAT:.*", text)
			for f in fragment_results:
				genre = f.split("CAT: ")
				genre = genre[1].split("'")
				genre = genre[0]
				print("- Found genre [%s]" % genre)
				return genre
		except Exception as e:
			print("- Unable to extract game genre from fragment")
			print(e)
			
		return genre
	
	def get_rating_from_fragment(self, text = ""):
		
		# Rating is in a json block within the text...
		#
		# "ratingValue": "4.3"
		#
		rating = 0
		
		try:
			fragment_results = re.findall("ratingValue.*", text)
			for f in fragment_results:
				rating = f.split(':')
				rating = rating[1].split('"')
				rating = float(rating[1])
				rating = rating / 5
				print("- Found rating [%s]" % rating)
				return rating
		except Exception as e:
			print("- Unable to extract game rating from fragment")
			print(e)
			
		return rating
	
	def get_date_from_fragment(self, text = ""):
		
		release_date = ""
		
		try:
			if self.data_block:
				date = self.data_block['globalReleaseDate']
				print("- Found release date (data block) [%s]" % date)
				return date
			else:
				fragment_results = re.findall("globalReleaseDate\":\"....-..-..T..:..:..", text)
				for f in fragment_results:
					date = f.split('"')
					date = date[2]
					print("- Found release date (regex) [%s]" % date)
					return date
		except Exception as e:
			print("- Unable to extract game release date from fragment")
			print(e)
			
		return release_date
	
	def get_players_from_fragment(self, text = ""):
		# Almost impossible to get from the html, as it looks like this:
		#
		# <svg class="details__feature-icon details__feature-icon--single"><use xlink:href="#single"></use></svg>
		# Single-player
		#
		# No class or id that uniquely identifies this block :(
		
		return 1
	
	def get_title_from_fragment(self, text = ""):
		""" Return game title """
		name = None
	
		if self.data_block:
			name = self.data_block['title']
			print("- Found title %s" % name)
			return name
		else:
			print("- Title extraction is only possible if we have extracted the GOG embedded json data!")
			return False
	
	def get_cover(self):
		""" Extract game cover art """
		
		if self.data_block:
			cover = self.data_block['boxArtImage']
			print("- Found cover %s" % cover)
			print("- Found covert art URL (data block)")
			return cover
		else:
			print("- Art extraction is only possible if we have extracted the GOG embedded json data!")
			return False
			
	def get_marquee(self):
		""" Extract game marquee/transparent game logo/title """
		
		if self.data_block:
			cover = self.data_block['logo']
			print("- Found title/marquee %s" % cover)
			print("- Found title/marquee art URL (data block)")
			return cover
		else:
			print("- Art extraction is only possible if we have extracted the GOG embedded json data!")
			return False
		
	def get_title(self):
		""" Extract game marquee/transparent game logo/title """
		# Not supported on GOG titles
		return False
		
	def get_screen(self):
		""" Extract screenshots """
		
		if self.data_block:
			covers = self.data_block['screenshots']
			for c in covers:
				print("- Found screenshot:  %s.jpg" % c['imageUrl'])
			print("- Found title/marquee art URL (data block)")
			if len(covers) > 0:
				return covers[0]['imageUrl'] + ".jpg"
			else:
				return False
		else:
			print("- Art extraction is only possible if we have extracted the GOG embedded json data!")
			return False
			
	def get_video(self):
		""" Extract videos """
		
		youtube_videos = []
		
		if self.data_block:
			videos = self.data_block['videos']
			for v in videos:
				if v['provider'] != 'youtube':
					print("- Found video %s [unsupported video source: %s]" % (v['url'], v['provider']))
				else:
					print("- Found video %s" % (v['url']))
					youtube_videos.append(v['url'])
		else:
			print("- Art extraction is only possible if we have extracted the GOG embedded json data!")
			return False
	
		if len(youtube_videos) > 0:
			return youtube_videos[0]
			
	def download_video(self, game = None, download_path = "", enable_overwrite = False):
		""" Download a video """
		
		ptw = PTWrapper()
		ptw.download(game, download_path, "video", enable_overwrite)