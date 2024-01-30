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
		
	def add_game(self, game, enable_overwrite = False):
		""" Add a game to the xml file """
		
		if self.xml_path:
			
			if self.is_parsed:
				pass
			else:
				self.init_xml()
			
			updated = False
			
			# Open xml
			tree = etree.parse(self.xml_path)
			root = tree.getroot()
			
			# Create new entry
			game_element = etree.Element('game')
			
			path_el = etree.Element('path')
			path_el.text = game['path']
			game_element.append(path_el)
			
			process_fields = ['name', 'description', 'rating', 'date', 'developer', 'publisher', 'genre', 'players']
			for k in process_fields:
				if game[k]:
					el = etree.Element(k)
					el.text = str(game[k])
					game_element.append(el)
					updated = True
				
			# Add new entry
			root.append(game_element)
			
			# Close xml
			if updated:
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
			tree = etree.parse(self.xml_path)
			root = tree.getroot()
			
			updated = False
			
			# Find existing entry
			for game_element in root.findall('game'):	
				game_path = game_element.find('path').text
				if (game_path == game['path']):
					# Found the matching game
				
					# Change attributes
					if enable_overwrite:
						# Update all fields
						process_fields = ['name', 'description', 'rating', 'date', 'developer', 'publisher', 'genre', 'players']
					else:
						# Find only missing/empty fields
						process_fields = []
						for f in ['name', 'description', 'rating', 'date', 'developer', 'publisher', 'genre', 'players']:
							element_field = game_element.find(f)
							if (element_field is None):
								process_fields.append(f)
								
					# Update any fields
					if len(process_fields) > 0:
						print("- Processing: %s" % process_fields)
						for k in process_fields:
							if game[k]:
								el = etree.Element(k)
								el.text = str(game[k])
								game_element.append(el)
								updated = True
					else:
						print("- No additional missing fields found")
						
			# Close xml
			if updated:
				tree_string = etree.tostring(root, encoding="unicode")
				reparsed = minidom.parseString(tree_string)
				f = open(self.xml_path, "w")
				f.write(tree_string)
				f.write("\n")
				f.close()