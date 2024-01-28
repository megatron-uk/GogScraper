#!/usr/bin/env python3

################################
#
# Works with gamelist.xml as used
# by EmulationStation
#
#################################

import os
import xml.etree.ElementTree as etree
from xml.dom import minidom

class Gamelist():
	
	def __init__(self, xml_path = ""):
		self.xml_path = xml_path
		self.is_parsed = False
		if os.path.isfile(self.xml_path):
			pass
		else:
			self.init_xml()
	
	def init_xml(self):
		try:
			print("- Creating new gamelist.xml %s" % self.xml_path)
			tree = etree.Element('GameList')
			tree_string = etree.tostring(tree, 'utf-8')
			reparsed = minidom.parseString(tree_string)
			f = open(self.xml_path, "w")
			f.write(reparsed.toprettyxml(indent="   "))
			f.write("\n")
			f.close()
			self.is_parsed = True
		except Exception as e:
			print("- Unable to create new gamelist.xml")
			print(e)
			return False
	
	def games(self):
		""" Return full list of games; one dict per game """
		pass
	
	def names(self):
		""" Return full list of game names """
		# Game 'names' are really the rom filenames
		#
		# Setting the 'flat' parameter will strip leading slashes
		# and any file extension suffixes
		#
		# e.g. "./Final Fantasy VII.lnk"
		# becomes
		# "Final Fantasy VII"
		
		games = []

		if self.xml_path:
			try:
				tree = etree.parse(self.xml_path)
				root = tree.getroot()
				for pathname in root.iter('path'):
					filename = pathname.text.replace('./', '')
					games.append(filename)
			except Exception as e:
				print("- No entries found, gamelist.xml is possibly blank")
		
		return games
		
	def add_game(self, game):
		""" Add a game to the xml file """
		
		if self.xml_path:
			
			if self.is_parsed:
				pass
			else:
				self.init_xml()
			
			# Open xml
			tree = etree.parse(self.xml_path)
			root = tree.getroot()
			
			# Create new entry
			game_element = etree.Element('game')
			
			path_el = etree.Element('path')
			path_el.text = game['path']
			game_element.append(path_el)
			
			if game['realname']:
				name_el = etree.Element('name')
				name_el.text = game['realname']
				game_element.append(name_el)
			
				if game['description']:
					desc_el = etree.Element('description')
					desc_el.text = game['description']
					game_element.append(desc_el)
				
				if game['rating']:
					rating_el = etree.Element('rating')
					rating_el.text = str(game['rating'])
					game_element.append(rating_el)
				
				if game['date']:
					releasedate_el = etree.Element('date')
					releasedate_el.text = game['date']
					game_element.append(releasedate_el)
				
				if game['developer']:
					developer_el = etree.Element('developer')
					developer_el.text = game['developer']
					game_element.append(developer_el)
				
				if game['publisher']:
					publisher_el = etree.Element('publisher')
					publisher_el.text = game['publisher']
					game_element.append(publisher_el)
				
				if game['genre']:
					genre_el = etree.Element('genre')
					genre_el.text = game['genre']
					game_element.append(genre_el)
				
				if game['players']:
					players_el = etree.Element('players')
					players_el.text = str(game['players'])
					game_element.append(players_el)
				
			# Add new entry
			root.append(game_element)
			
			# Close xml
			tree_string = etree.tostring(root, encoding="unicode")
			reparsed = minidom.parseString(tree_string)
			f = open(self.xml_path, "w")
			f.write(tree_string)
			f.write("\n")
			f.close()
	
	def update_game(self, game, enable_overwrite = False):
		""" Amend an existing game in the xml file """
		
		if self.xml_path:
			# Open xml
			# Find existing entry
			# Change attributes
			# Close xml
			pass