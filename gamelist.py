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
		if os.path.isfile(xml_path):
			pass
		else:
			try:
				print("- Creating new gamelist.xml %s" % xml_path)
				tree = etree.Element('GameList')
				tree_string = etree.tostring(tree, 'utf-8')
				reparsed = minidom.parseString(tree_string)
				f = open(xml_path, "w")
				f.write(reparsed.toprettyxml(indent="   "))
				f.close()
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
			# Open xml
			tree = etree.parse(self.xml_path)
			root = tree.getroot()
			
			# Add new entry
			# Close xml
			pass
	
	def update_game(self, game):
		""" Amend an existing game in the xml file """
		
		if self.xml_path:
			# Open xml
			# Find existing entry
			# Change attributes
			# Close xml
			pass