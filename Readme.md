# GogScraper

A game data scraper for [EmulationStation](https://emulationstation.org/), [EmulationStation DE](https://es-de.org/) and similar systems which use gamelist.xml data ([RetroArch](https://www.retroarch.com/), for example).

Primarily for **PC games** (i.e. those on Windows/Linux/Mac) which are not already well served by such databases as [Screenscraper](https://www.screenscraper.fr/), [TheGamesDB](https://thegamesdb.net/) and the like.

Whilst the above sources are fairly good - they have a lot of holes, especially for indie titles that are available on GOG.com.

This tool is intended to retrieve full information about games which have been bought from [GOG.com](https://www.gog.com). Since the games are from GOG.com, then that has surely got to be the best place to get information about them!

This *may* be expanded in the future to support games from [Steam](https://store.steampowered.com/).

Currently supports the following features

   * Can search for games in GOG.com using the shortcuts in your EmulationStation folder (either Windows **.lnk** or Linux **.desktop** format)
   * Multiple results prompt for user to select the correct game; exact matches are auto selected.
   * From a matching game page on GOG.com, the following can be retrieved automatically:
      * Game **metadata** is downloaded (title, developer, publisher, release date, rating, genre).
      * Game **artwork** is downloaded (marquee image, cover art, screenshot).
      * Game **video** is downloaded (YouTube based linked videos only).
   * Gamelist.xml is updated automatically with new entries or updated metadata for each game.

---

### How it works

The application searches a given folder from your EmulationStation installation (normally the folder in which you have your PC game shortcuts, which is the reccomended way of importing PC/desktop games to your EmulationStation/RetroArch front end). 

- The title of the Windows shortcut/Linux desktop file (minus any extension) is used to run a live search against the GOG.com games library.

- The HTML results from the call to the GOG.com are parsed, and exact matches are used to proceed to the next step. If multiple results are returned, a prompt is shown to the user of all possible matches.

- Once a match is made, another call is made to the URL of the matching game. The retrieved HTML is parsed, several items of metadata are extracted from the HTML document, with artwork and other remaining metadata pulled from an embedded JSON data structure within the page.

- The metadata can (optionally) be used to fill in blanks in the gamelist.xml file.

- The artwork (cover, marquee, screenshot) can (optionally) be downloaded to the relevant media folders.

- The video (if available) can (optionally) be downloaded to the relevant media folder.

---

## Using the tool

### Requirements

- Python 3.x
- requests*
- beautifulsoup4*
- pytube*

Starred items are defined in the **requirements.txt** file.

As long as you have Python 3 installed, download the code from this project, and in a command terminal, type:

```
pip3 install -r requirements.txt
```

That's it. No other external dependencies are needed. The code should work the same on Windows, Linux and Mac.

### Running the tool

The tool is run from the **scrape.py** script. Run this with Python 3 without any options to get a list of all available commands:

```
$ python3 scraper.py

$ Scraper running...
usage: scrape.py [-h] [-d] [-a] [-v] [-f] --roms ROM_PATH --xml XML_PATH --media DOWNLOAD_PATH
scrape.py: error: the following arguments are required: --roms, --xml, --media
$
```

You can use the **-h** (help) flag to show more details:

```
$ python3 scrape.py -h
Scraper running...
usage: scrape.py [-h] [-d] [-a] [-v] [-f] --roms ROM_PATH --xml XML_PATH --media DOWNLOAD_PATH

Scrape media and metadata for games in an EmulationStation folder.

options:
  -h, --help            show this help message and exit
  -d, --enable-data     Enable text metadata downloading & extraction
  -a, --enable-art      Enable artwork (screens, titles, marquee, covers) image downloading
  -v, --enable-video    Enable video downloading (Youtube only)
  -f, --force           Force overwrite of any existing artwork, video or metadata for each game
  --roms ROM_PATH       Set the path to the folder of games/links/shortcuts you want to process
  --xml XML_PATH        Set the full path and filename of the gamelist.xml you wish to process
  --media DOWNLOAD_PATH
                        Set the path to store downloaded media
```

*Note: If you do not already have a gamelist.xml file for your desktop game collection, this tool will generate one for you, to the EmulationStation specification, based on the results it finds.*

By default, the tool will only perform searches and show search results - it **must** be instructed to try to download metadata, artwork or videos.

Even when metadata, artwork or video downloading is enabled (by **-d**, **-a** and **-v**), the tool will refuse to overwrite any existing entries in your gamelist.xml, or any existing art/video files in your media folders. If you wish to force (re)downloading of data to overwrite any existing local content you must supply the **-f** (force) flag.

### Examples

#### 1. Do it all, but retain any existing content

Probably the most common example is to search all games and download any missing data, art and videos.

- Roms/Shortcuts folder in **/games/desktop**
- Desktop gamelist.xml in **/home/user/.emulationstation/gamelists/desktop/gamelist.xml**
- Downloaded media in **/home/user/.emulationstation/downloaded_media/desktop**
- Download game metadata, adding any new entries if missing, will not change any existing fields
- Download artwork (marquees, covers, screenshots), if available, skipping if already present
- Download videos, if available, skipping if already present
- Will **not** overwrite any existing content

```
$ python3 scrape.py --roms /games/desktop --xml /home/user/.emulationstation/gamelists/desktop/gamelist.xml --media /home/user/.emulationstation/downloaded_media/desktop -d -a -v
```

#### 2. Force redownload of all metadata

If you want to force the rebuild of your gamelist.xml with fresh data, then this does **only** that.

- Roms/Shortcuts folder in **/games/desktop**
- Desktop gamelist.xml in **/home/user/.emulationstation/gamelists/desktop/gamelist.xml**
- Download game metadata
- **Force** overwriting of any existing entries in gamelist.xml

```
$ python3 scrape.py --roms /games/desktop --xml /home/user/.emulationstation/gamelists/desktop/gamelist.xml -d -f
```

### Example Output

#### 1. Automatic match against a single game

This example shows the scraper finding an exact match against a title, and autoamtically downloading metadata, art and video, and then finally creating a missing entry in the gamelist.xml file. In this example the process is entirely automatic:

```
$ ./scrape.py --roms ./test_roms/desktop/ --xml ./test_xml/desktop/gamelist.xml --media ./test_media/desktop -d -a -v
Scraper running...

Selected options: [data: True] [art: True] [video: True] [overwrite: False]
ROM path: ./test_roms/desktop/
XML path: ./test_xml/desktop/gamelist.xml
Media path: ./test_media/desktop

Getting game names from ./test_roms/desktop/:
- Found [3] 

Getting game names from gamelist.xml ./test_xml/desktop/gamelist.xml:
- Found [0] 

Searching GOG.com for Hyper Light Drifter:
- Found [1]

ID | Name                                                                   | URL
-- | -----                                                                  | -----
 0 | Hyper Light Drifter                                                    | https://www.gog.com/en/game/hyper_light_drifter

Got one exact match!

Continuing with ID 0, Hyper Light Drifter

Retrieving game data from GOG.com for https://www.gog.com/en/game/hyper_light_drifter:
- Returned 654320 bytes
- Extracted GOG.com embedded json data
- Found description (regex)
- Found developer
- Found publisher
- Found genre
- Found rating
- Found release date (data block)
- Found video https://fast.wistia.net/embed/iframe/2uklcaqota [unsupported video source: wistia]
- Found video https://fast.wistia.net/embed/iframe/za8qg28t0p [unsupported video source: wistia]
- Found video https://www.youtube.com/embed/KkiDLv8DJPk?wmode=opaque&rel=0
- Found video https://www.youtube.com/embed/Gh2bbiHfc5c?wmode=opaque&rel=0
- Found screenshot:  https://images.gog-statics.com/df95e4fcd025df794066397c3c0faa05fe0aac4a98ceb4e25a199e0d9a5b53b2.jpg
- Found screenshot:  https://images.gog-statics.com/8d717ee7e4be9df31abe7de05f37da675864ce6ded4bb93a93bee97d49a28f05.jpg
- Found screenshot:  https://images.gog-statics.com/a2b778aabc2e6e81dafa1cc1b9a13aa6ca455150f2bbdf441205b9fffc23ef6c.jpg
- Found screenshot:  https://images.gog-statics.com/8f4417f395149342e482585d7bcfb5abaeefc77f5489b3e9853798e951192c14.jpg
- Found screenshot:  https://images.gog-statics.com/3f2e29cdfc64063cd15f766f73f740d071850449f2665c579e7065f0df81a540.jpg
- Found screenshot:  https://images.gog-statics.com/d54a18928f360fa6a235e40382a38ed245be80c59b1caf6f8c77022907fbdb27.jpg
- Found screenshot:  https://images.gog-statics.com/1a3ea40ca67c5df6eea92b50b61138470c686f08677d99e0610ed027c2d18109.jpg
- Found screenshot:  https://images.gog-statics.com/ebf91578dfab871d14a7913edd2cdb2caeaaea1ef38a21647a8644485ddb9da9.jpg
- Found screenshot:  https://images.gog-statics.com/4342b8e4406bf5137a74d65b201c8b97791e3bd050bfe431562ca605e0946a3b.jpg
- Found screenshot:  https://images.gog-statics.com/8afedb657c19b09567d123b459401db766d4d72d630b1f44437155b173528e7d.jpg
- Found screenshot:  https://images.gog-statics.com/bbd549923c0884d6896035d0607923aba42d34d8a49febc2f5b256529a4ca0a3.jpg
- Found screenshot:  https://images.gog-statics.com/ddc262a0f68ffe37786a6d56f58772b186eb6dc9e99dc62bd9ad91b74023b900.jpg
- Found screenshot:  https://images.gog-statics.com/a8cc1d710514062663a782b896bb9d5daa81df4a5966d979607f67354155a242.jpg
- Found title/marquee art URL (data block)
- Found title/marquee https://images.gog-statics.com/350c2a57c8f9cb311c387fb8ed193b4a28c972da4730c82134019e6da8a73cdd.png
- Found title/marquee art URL (data block)
- Found cover https://images.gog-statics.com/070a0da8ce5bb2ebe64880357c27208bb5b2d3c68a4d13a95f37afbbe7122360.jpg
- Found covert art URL (data block)

Downloading external art assets
- Downloading screens
- ... downloaded ./test_media/desktop/screenshots/Hyper Light Drifter.jpg
- Downloading marquee
- ... downloaded ./test_media/desktop/marquees/Hyper Light Drifter.jpg
- Downloading cover
- ... downloaded ./test_media/desktop/covers/Hyper Light Drifter.jpg

Downloading external video assets
- Downloading 480p stream
- Error attempting to download https://www.youtube.com/embed/KkiDLv8DJPk?wmode=opaque&rel=0 [480p]
'NoneType' object has no attribute 'download'
- Downloading 720p stream
- ... downloaded ./test_media/desktop/videos/Hyper Light Drifter.mp4

Updating gamelist.xml metadata
- Creating new gamelist.xml entry
```
We can see in the above example that no 480P video stream is found (the first format attempted), and the tool then proceeds to download the next resolution option, 720P.

If the same script was ran a second time, then *without* the **-f** (force) parameter, all of the newly downloaded data and artwork would be skipped. So this is the safest way to run the tool.


#### 2. Manual Selection of Results

In the below example we can see multiple results for a game in our collection. We will need to select the ID of one of the games before the tool can continue:

```
$ ./scrape.py --roms ./test_roms/desktop/ --xml ./test_xml/desktop/gamelist.xml --media ./test_media/desktop -d -a -v
Scraper running...

Selected options: [data: True] [art: True] [video: True] [overwrite: False]
ROM path: ./test_roms/desktop/
XML path: ./test_xml/desktop/gamelist.xml
Media path: ./test_media/desktop

Getting game names from ./test_roms/desktop/:
- Found [3] 

Getting game names from gamelist.xml ./test_xml/desktop/gamelist.xml:
- Found [0] 
- 
Searching GOG.com for Batman - Arkham Knight:
- Found [2]

ID | Name                                                                   | URL
-- | -----                                                                  | -----
 0 | Batman - Arkham Knight                                                 | https://www.gog.com/en/game/batman_arkham_knight_premium_edition
 1 | Batman - Arkham Knight                                                 | https://www.gog.com/en/game/batman_arkham_knight

Enter an ID to use the metadata and media from that title.
(Hint: Control+Click on the URL to open the page in your browser)
```

At this point you would have to enter the correct ID to choose the most relevant search result. The tool would then continue automatically with the metadata download and extraction and artwork/video as normal.

---

## Artwork & Video Details

### Screenshots

Currently, EmulationStation only supports a single artwork file for each category (title screen, box cover, marquee, screenshot). Since GOG.com lists multiple screenshots for a game, it is an arbitrary decision on which is downloaded. The tool does not make any attempt to 'guess' which should be the best, it simply downloads the first in the list of screenshots embedded within the page. While downloading metadata and artwork, a list of all found image URLs are shown, if you wish to download any yourself as alternatives.

### Videos

As with screenshots, it is possible that multiple video files (or none at all) may be listed against a game on GOG.com. Again we have no means of determining which is 'best', as with screenshots, we just download the first entry. All found video URLs are displayed during download, if you wish to download any yourself as alternatives.

The linked YouTube videos may be of varying stream quality. The order in which we attempt to download the various quality streams is defined in **pytubewrapper.py** if you want to customise the sequence in which it tries to download the files. This is nominally a *480P* stream, then *720P* and finally *360P*; remember these are only shown at approximately quarter-screen within EmulationStation and similar front ends.

*Note: Only YouTube linked videos are supported. Some GOG.com titles have videos linked to other streaming services and these are not currently supported for download.*