#!/usr/bin/env python3

#######################################
#
# Wrapper around pytube (https://pytube.io/en/latest/index.html)
# to download videos as linke from GOG.com
# and other pages.
#
#######################################

import os
from pytube import YouTube

# Video size steps
video_steps = ["480p", "720p", "360p"]

class PTWrapper():
	
	def __init__(self):
		pass
	
	def download(self, game = None, download_path = "", art_type = "video", enable_overwrite = False):
		""" Try to download a video from the url given """
		
		if (game['video']):
			for res in video_steps:
				try:
					print("- Downloading %s stream" % res)
					path = os.path.join(download_path, "videos")
					filename = game['filename'] + ".mp4"
					if (os.path.isfile(os.path.join(path, filename))) and (enable_overwrite is False):
						print("- ... already exists, skipping (Hint: -f to overwrite)")
						return False
					else:
						y = YouTube(game['video'])
						s = y.streams.get_by_resolution(res)
						s.download(output_path = path, filename = filename)
						print("- ... downloaded %s" % (path + "/" + filename))
						return True
						
				except Exception as e:
					print("- Error attempting to download %s [%s]" % (game['video'], res))
					print(e)
		else:
			print("- Error, no video stream present? Bug?")
			return False
	