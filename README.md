# AudioNow scraper extension for gPodder
This project is an unofficial Extension for gPodder which adds support to [AudioNow](https://audionow.de/)  podcasts.

### Dependencies
`gPodder`: As this is an extension for gPodder, obviously gPodder needs to be installed


### Installation
There is a guide how to install gPodder extensions [here](https://gpodder.github.io/docs/extensions.html).

Short summary for Linux/macOS users:
 - Create `~/gPodder/Extensions` folder (if it does not exist)
 - Place the `audionow_scraper.py` in this folder as `~/gPodder/Extensions/audionow_scraper.py`
 - Restart gPodder (if it was running)
 - Activate the extension with the name "AudioNow Source" in the gPodder UI:
   - Click the three points in the right upper and select "Preferences"
   - Go to "Extensions"
   - Now, under category "Other" there should be an entry with AudioNow Source. This needs to be activated.

### Usage
To use this gPodder extension, make sure that it is installed.
After installation, you can include any link from an AudioNow podcast with the "Add podcast via URL" link.
[Here](https://audionow.de/podcast) you can find a list of Podcast and choose a link from there.


### Credits
First of all I want to credit gPodder and the Extension system. Without this system, the extension would have been much more complicated. 
This plugin is based on the "Hello World" example as well as the "Soundcloud" Extension for gPodder.