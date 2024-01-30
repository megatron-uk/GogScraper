#!/usr/bin/env python3

##########################################
#
# Search for a game on gog.com and scrape
# any metadata, as used by emulationstation.
#
##########################################

# Builtins and site packages
import argparse
import xml.etree.ElementTree as etree
import os
import requests
import sys

# Scraper types
from gog import GOG as GProvider
from steam import Steam as SProvider
from gog import MEDIA as GMEDIA
from steam import MEDIA as SMEDIA

# Gamelist.xml helper
from gamelist import Gamelist

def get_roms_list(path = ""):
	""" Get the list of roms/files in a given directory """
	
	games = []
	
	print("")
	print("Getting game names from %s:" % path)
	
	files = os.listdir(path)
	for f in files:
		if os.path.isfile(os.path.join(path,f)):			
			games.append(f)
	
	print("- Found [%d] " % len(games))
	return games

def get_rom_stripped_name(game_name = ""):
	""" Strip any extraneous extensions of the game names """
	
	g = game_name.replace('.desktop', '')
	g = g.replace('.lnk', '')
	g = g.replace('.LNK', '')
	g = g.replace('./', '')
		
	return g

def download_or_overwrite_art(game, download_path, art_type, overwrite):
	
	if art_type == "screens":
		path = os.path.join(download_path, "screenshots")
		
	if art_type == "cover":
		path = os.path.join(download_path, "covers")
		
	if art_type == "marquee":
		path = os.path.join(download_path, "marquees")
		
	if art_type == "title":
		path = os.path.join(download_path, "titlescreens")
		
	filename = game['filename'] + ".jpg"
		
	if game[art_type]:
		print("- Downloading %s" % art_type)
		
		if os.path.isdir(path):
		
			if os.path.isfile(os.path.join(path, filename)) and (overwrite is False):
				print("- ... already exists, skipping (Hint: -f to overwrite)")
				return
			
			r = requests.get(game[art_type], stream=True)
			if (r.status_code == 200):
				f = open(path + "/" + filename, "wb")
				for chunk in r.iter_content(chunk_size=128):
					f.write(chunk)
				f.close()
				print("- ... downloaded %s" % (path + "/" + filename))
				
		else:
			print("- Error, download path %s does not exist" % path)
	
	return
	

def exit_abnormal(code, msg):
	""" Exit abnormally """
	
	print(msg)
	print("")
	print("Scraper will now exit.")
	sys.exit(code)

if __name__ == "__main__":

	print("Scraper running...")

	parser = argparse.ArgumentParser(description='Scrape media and metadata for games in an EmulationStation folder.', add_help = True)
	
	# Flag to enable metadata download/setting
	parser.add_argument('-d', '--enable-data', dest='enable_data', action='store_true', help='Enable text metadata downloading')
	
	# Enable artwork downloading
	parser.add_argument('-a', '--enable-art', dest='enable_art', action='store_true', help='Enable artwork (screens, titles, marquee, covers) image downloading')
	
	# Enable video downloading
	parser.add_argument('-v', '--enable-video', dest='enable_video', action='store_true', help='Enable video downloading (Youtube only)')

	# Enable data/media over-writing
	parser.add_argument('-f', '--force', dest='enable_overwrite', action='store_true', help='Force overwrite of any existing artwork, video or metadata for each game')

	# Name of folder to process
	parser.add_argument('--roms', dest='rom_path', action='store', required=True, help='Set the path to the folder of games you want to process')

	# Path to gamelist
	parser.add_argument('--xml', dest='xml_path', action='store', required=True, help='Set the full path and filename of the gamelist.xml you wish to process')
	
	# Path to downloaded media directory
	parser.add_argument('--media', dest='download_path', action='store', required=True, help='Set the path to store downloaded media')
	
	parser.add_argument('--provider', dest='provider', action='store', required=True, help='Set the data provider to "gog" or "steam"')
	
	args = parser.parse_args()
	args_dict = vars(args)
	enable_data = args_dict['enable_data']
	enable_art = args_dict['enable_art']
	enable_video = args_dict['enable_video']
	enable_overwrite = args_dict['enable_overwrite']
	provider = args_dict['provider']
	rom_path = args_dict['rom_path']
	xml_path = args_dict['xml_path']
	download_path = args_dict['download_path']
	
	print("")
	print("Selected options: [data: %s] [art: %s] [video: %s] [overwrite: %s]" % (enable_data, enable_art, enable_video, enable_overwrite))
	print("Data provider: %s" % provider)
	print("ROM path: %s" % rom_path)
	print("XML path: %s" % xml_path)
	print("Media path: %s" % download_path)
	
	if provider.upper() not in ["GOG", "STEAM"]:
		exit_abnormal(1, "You must set the provider to be either 'gog' or 'steam'")
	
	if provider.upper() == "GOG":
		p = GProvider(debug = False)
		if p is False:
			exit_abnormal(1, "The GOG.com provider could not be initialised.")
		MEDIA = GMEDIA
	if provider.upper() == "STEAM":
		p = SProvider(debug = False)
		if p is False:
			exit_abnormal(1, "The Steam provider could not be initialised.")
		MEDIA = SMEDIA
	
	# Get a list of all games/roms in the rom folder
	games_list = get_roms_list(rom_path)
	
	# Get a list of all games/roms in the xml file
	print("")
	print("Getting game names from gamelist.xml %s:" % xml_path)
	gl = Gamelist(xml_path)
	if gl is False:
		exit_abnormal(1, "Unable to open or create gamelist.xml")
	else:
		games_xml_list = gl.names()
		print("- Found [%d] " % len(games_xml_list))
	
	# Default is to search for games with no metadata
	#games_missing_data = []
	
	# We can also search for games with no artwork
	#games_missing_art = []
	
	# Or we can just search for games with no video
	#games_missing_video = []
	
	# We search using the filename, stripped of any suffix
	for g in games_list:	
		
		idx = 0
		
		game_matches = []
		
		# Get the search page results
		g_s = get_rom_stripped_name(g)
		search_results = p.get_search(g_s)
		
		# For each game object in the page of results....
		for result in search_results:
			
			data = {
				'id' : idx,	
				'provider_id' : False,
				'url' : "",
				'path' : g,
				'name' : g_s,
				'filename' : g_s,
				'description' : "",
				'date' : "",
				'developer' : "",
				'publisher' : "",
				'genre' : "",
				'players' : 1,
				'video' :  False,
				'screens' :  False,
				'cover' : False,
				'marquee' : False,
				'title' : False,
				'has_xml' : False,
			}

			# Store the steam appid
			if provider.upper() == "STEAM":
				data['provider_id'] = result['appid']

			# Does this title already have a gamelist.xml entry?
			if g in games_xml_list:
				data['has_xml'] = True

			# Try to extract real game name
			# and use it to replace the stripped filename
			n = p.get_gamename_from_fragment(result)
			if n:
				data['name'] = n

			# Try to extract URL to game page
			data['url'] = p.get_href_from_fragment(result, url_type = "game")

			# Add this game entry
			game_matches.append(data)
			
			# Increment result ID
			idx += 1
			
		print("")
		print("%2s | %-70s | %s" % ("ID", "Name", "URL"))
		print("%2s | %-70s | %s" % ("--", "-----", "-----"))
		for game in game_matches:
			print("%2d | %-70s | %s" % (game['id'], game['name'], game['url']))
			
		# If we have only one match, and it is an exact match, then continue
		if (len(game_matches) == 1) and (game_matches[0]['name'].upper() == g_s.upper()):
			continue_id = game_matches[0]['id']
			game = game_matches[0]
			print("")
			print("Got one exact match!")
		else:
			game = False
			continue_id = False
			
		if continue_id is False:
			print("")
			print("Enter an ID to use the metadata and media from that title.")
			print("(Hint: Control+Click on the URL to open the page in your browser)")
			print("")
			i = input()
			
			# Make sure this is the ID of a game we found
			found = False
			game = False
			if i:
				for g in game_matches:
					if int(i) == g['id']:
						found = True
						game = g
			if game is False:
				print("")
				print("Sorry, that is not a valid found game ID")
				
		if game:
			print("")
			print("Continuing with ID %s, %s" % (game['id'], game['name']))
			game_html = p.get_game(game, game_url = game['url'])
			
			if game_html:
				
				# Update
				p.get_data(game['url'], game_html)
				
				# Basic metadata
				if MEDIA['data']:
					game['realname'] = p.get_title_from_fragment(game_html)
					game['desc'] = p.get_description_from_fragment(game_html)
					game['developer'] = p.get_developer_from_fragment(game_html)
					game['publisher'] = p.get_publisher_from_fragment(game_html)
					game['genre'] = p.get_genre_from_fragment(game_html)
					game['rating'] = p.get_rating_from_fragment(game_html)
					game['date'] = p.get_date_from_fragment(game_html)
					game['players'] = p.get_players_from_fragment(game_html)
					for k in ['desc', 'developer', 'publisher', 'name', 'realname']:
						if game[k]:
							game[k] = str(game[k]).encode("ascii", "replace").decode(encoding='ascii')
				# Video
				if MEDIA['video']:
					if enable_video:
						game['video'] = p.get_video()
					else:
						print("- Video downloads are disabled (Hint: -v to retrieve video)")
				else:
					print("- Provider does not support video")
				
				# Title screen
				if MEDIA['title']:
					if enable_art:
						game['title'] = p.get_title()
					else:
						print("- Title artwork downloading is disabled (Hint: -a to retrieve artwork)")
				else:
					print("- Provider does not support title screens")
				
				# Screenshot
				if MEDIA['screens']:
					if enable_art:
						game['screens'] = p.get_screen()
					else:
						print("- Screenshot downloading is disabled (Hint: -a to retrieve artwork)")
				else:
					print("- Provider does not support screenshots")
				
				# Marquee
				if MEDIA['marquee']:
					if enable_art:
						game['marquee'] = p.get_marquee()
					else:
						print("- Marquee artwork downloading is disabled (Hint: -a to retrieve artwork)")
				else:
					print("- Provider does not support marquee images")
				
				# Cover art
				if MEDIA['cover']:
					if enable_art:
						game['cover'] = p.get_cover()
					else:
						print("- Cover artwork downloading is disabled (Hint: -a to retrieve artwork)")
				else:
					print("- Provider does not support cover or box art")
			
			# Download external media
			if (enable_art):
				print("")
				print("Downloading external art assets")		
				for art_type in ["screens", "title", "marquee", "cover"]:
					download_or_overwrite_art(game, download_path, art_type, enable_overwrite)

			if (enable_video):
				print("")
				print("Downloading external video assets")
				p.download_video(game, download_path, "video", enable_overwrite)
				
			# Update xml metadata
			if (enable_data):
				print("")
				print("Updating gamelist.xml metadata")
				if (game['has_xml']):
					# Find and edit existing entry
					if (enable_overwrite):
						print("- Updating existing gamelist.xml entry")
					else:
						print("- Updating existing gamelist.xml entry (missing fields only)")
					gl.update_game(game, enable_overwrite)
				else:
					# Add new entry
					print("- Creating new gamelist.xml entry")
					gl.add_game(game, enable_overwrite)
					
				# Update the list of games with XML, in case we find a match in any
				# subsequent loops
				games_xml_list = gl.names()