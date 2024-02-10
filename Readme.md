# GogScraper

A game data scraper for [EmulationStation](https://emulationstation.org/), [EmulationStation DE](https://es-de.org/) and similar systems which use gamelist.xml data ([RetroArch](https://www.retroarch.com/), for example).

Primarily for **PC games** (i.e. those on Windows/Linux/Mac) which are not already well served by such databases as [Screenscraper](https://www.screenscraper.fr/), [TheGamesDB](https://thegamesdb.net/) and the like.

Whilst the above sources are fairly good - they have a lot of holes, especially for indie titles that are available on GOG.com or the Steam store.

This tool is intended to retrieve full information about games which have been bought from [GOG.com](https://www.gog.com) or [Steam](https://store.steampowered.com/). Since the games are bought from there, then those stores have surely got to be the best place to get information about them!

Currently supports the following features

   * Can search for games in **GOG.com or the Steam store** using the shortcuts in your EmulationStation folder (either Windows **.lnk** or Linux **.desktop** format)
   * Multiple search results will prompt the user to select the correct game; exact matches are auto selected.

   * From a matching game page on GOG.com, the following can be retrieved automatically:
      * Game **metadata** is downloaded (title, developer, publisher, release date, rating, genre).
      * Game **artwork** is downloaded (marquee image, cover art, screenshot).
        * Screenshots use the *first* of the listed images under 'screenshots'
        * Covers use the 'boxArtImage' image
        * Marquees use the 'logo' image
      * Game **video** is downloaded.
        * Uses the *first* listed video under 'videos'
        * Defaults to 480P, then 720P, then 360P resolution
        * YouTube based linked videos only
      
   * From a matching game in the Steam app data, the following can be retrieved automatically:
      * Game **metadata** is downloaded (title, developer, publisher, release date, rating, genre).
      * Game **artwork** is downloaded (marquee image, cover art, screenshot).
        * Screenshots use the *first* of the listed images under 'screenshots'
        * Covers use the 'header_image' image
        * Marquees use the 'capsule_image' image
      * Game **video** is downloaded (mp4 versions only).
        * Uses the *first* listed video under 'movies'
        * Defaults to 480P resolution
        * Defaults to MP4 containers 

   * Gamelist.xml is updated automatically with new entries *or* updated metadata for each game.
   * Can skip to a given letter in a directory of partially scraped games (i.e. start at 'S').
   * Can scrape a single named game in a directory of partially scraped games.

---

### How it works

The application searches a given folder from your EmulationStation installation (normally the folder in which you have your PC game shortcuts, which is the reccomended way of importing PC/desktop games to your EmulationStation/RetroArch front end). 

- The title of the Windows shortcut/Linux desktop file (minus any extension) is used to run a live search against the GOG.com games library/or a live downloaded list of games/game ID's from Steam.

- The HTML results from the call to the GOG.com are parsed, and exact matches are used to proceed to the next step. If multiple results are returned, a prompt is shown to the user of all possible matches. If it is a Steam game, and a match in the games ID's is found then we make a call to the Steam API page.

- Once a match is made against a GOG.com game, another call is made to the URL of the matching game. The retrieved HTML is parsed, several items of metadata are extracted from the HTML document, with artwork and other remaining metadata pulled from an embedded JSON data structure within the page. For a Steam game we download the JSON data direct from the Steam API.

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
usage: scrape.py [-h] [-d] [-a] [-v] [-f] --roms ROM_PATH --xml XML_PATH --media DOWNLOAD_PATH --provider PROVIDER
scrape.py: error: the following arguments are required: --roms, --xml, --media --provider
$
```

You can use the **-h** (help) flag to show more details:

```
$ python3 scrape.py --h
Scraper running...
usage: scrape.py [-h] [-d] [-a] [-v] [-f] --roms ROM_PATH --xml XML_PATH --media DOWNLOAD_PATH
                 --provider PROVIDER [--start-from START_FROM] [--rom ROM]

Scrape media and metadata for games in an EmulationStation folder.

options:
  -h, --help            show this help message and exit
  -d, --enable-data     Enable text metadata downloading
  -a, --enable-art      Enable artwork (screens, titles, marquee, covers) image downloading
  -v, --enable-video    Enable video downloading
  -f, --force           Force overwrite of any existing artwork, video or metadata for each game
  --roms ROM_PATH       Set the path to the folder of games you want to process
  --xml XML_PATH        Set the full path and filename of the gamelist.xml you wish to process
  --media DOWNLOAD_PATH
                        Set the path to store downloaded media
  --provider PROVIDER   Set the data provider to "gog" or "steam"
  --start-from START_FROM
                        Ignore all titles that start before this letter (use to skip initial games
                        in a partially scraped --roms folder)
  --rom ROM             Ignore all other titles found and process this rom filename only (use to
                        process only one game in the --roms folder). File extension not required.
```

*Note: If you do not already have a gamelist.xml file for your desktop game collection, this tool will generate one for you, to the EmulationStation specification, based on the results it finds.*

By default, the tool will only perform searches and show search results - it **must** be instructed to try to download metadata, artwork or videos.

Even when metadata, artwork or video downloading is enabled (by **-d**, **-a** and **-v**), the tool will refuse to overwrite any existing entries in your gamelist.xml, or any existing art/video files in your media folders. If you wish to force (re)downloading of data to overwrite any existing local content you must supply the **-f** (force) flag.

### Examples

#### 1. Use GOG.com - Do it all, but retain any existing content

Probably the most common example is to search all games and download any missing data, art and videos.

- Roms/Shortcuts folder in **/games/desktop**
- Desktop gamelist.xml in **/home/user/.emulationstation/gamelists/desktop/gamelist.xml**
- Downloaded media in **/home/user/.emulationstation/downloaded_media/desktop**
- Download game metadata, adding any new entries if missing, will not change any existing fields
- Download artwork (marquees, covers, screenshots), if available, skipping if already present
- Download videos, if available, skipping if already present
- Will **not** overwrite any existing content

```
$ python3 scrape.py --roms /games/desktop --xml /home/user/.emulationstation/gamelists/desktop/gamelist.xml --media /home/user/.emulationstation/downloaded_media/desktop --provider gog -d -a -v
```

#### 2. Use Steam - Force redownload of all metadata

If you want to force the rebuild of your gamelist.xml with fresh data, then this does **only** that.

- Roms/Shortcuts folder in **/games/desktop**
- Desktop gamelist.xml in **/home/user/.emulationstation/gamelists/desktop/gamelist.xml**
- Download game metadata
- **Force** overwriting of any existing entries in gamelist.xml

```
$ python3 scrape.py --roms /games/desktop --xml /home/user/.emulationstation/gamelists/desktop/gamelist.xml --provider steam -d -f
```

---

## Artwork & Video Details

### Screenshots

Currently, EmulationStation only supports a single artwork file for each category (title screen, box cover, marquee, screenshot). Since both GOG.com and Steam lists multiple screenshots for a game, it is an arbitrary decision on which is downloaded. The tool does not make any attempt to 'guess' which should be the best, it simply downloads the first in the list of screenshots embedded within the page. While downloading metadata and artwork, a list of all found image URLs are shown, if you wish to download any yourself as alternatives.

### Videos

As with screenshots, it is possible that multiple video files (or none at all) may be listed against a game on GOG.com and Steam. Again we have no means of determining which is 'best', as with screenshots, we just download the first entry. All found video URLs are displayed during download, if you wish to download any yourself as alternatives.

On GOG.com, the linked YouTube videos may be of varying stream quality. The order in which we attempt to download the various quality streams is defined in **pytubewrapper.py** if you want to customise the sequence in which it tries to download the files. This is nominally a *480P* stream, then *720P* and finally *360P*; remember these are only shown at approximately quarter-screen within EmulationStation and similar front ends.

With Steam, we automatically use the 480P MP4 videos linked in the JSON API data, since WEBM videos are not supported in EmulationStation.

*Note: Only YouTube linked videos are supported. Some GOG.com titles have videos linked to other streaming services and these are not currently supported for download.*