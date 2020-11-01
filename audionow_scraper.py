import datetime
import logging
import re
from collections import namedtuple
import time
from typing import Mapping

from lxml import html
from gpodder import model, feedcore, util, registry
from gpodder.model import PodcastChannel, PodcastEpisode

logger = logging.getLogger(__name__)

# Provide some metadata that will be displayed in the gPodder GUI.
__title__ = 'AudioNow Scraper'
__description__ = 'Use AudioNow as a source for Podcasts'
__only_for__ = 'gtk, cli'
__authors__ = 'Ruben Simons <ruben-github@sim0ns.de>'

Episode = namedtuple("Episode", ("audio_url", "description", "title", "guid", "date", "duration"))
Show = namedtuple("Show", ("episodes", "description", "title", "image_url"))


class AudioNowShow:
    def __init__(self, show):
        self.show = show

    @staticmethod
    def parse_html(html_code):
        tree = html.fromstring(html_code)
        description = tree.xpath('//div[@class="desc-text"]/p/text()')[0]
        image_url = tree.xpath('//meta[@property="og:image"]')[0].attrib['content']
        episodes = tree.xpath('//div[@class="podcast-episode"]')
        title = tree.xpath('//h1[@class="podcast-title"]/text()')[0]
        tagged_episodes = []
        for episode in episodes:
            title = episode.attrib['data-audiotitle']
            url = episode.attrib['data-audiolink']
            episode_description = "\n".join(episode.xpath('.//p/text()'))
            guid = episode.attrib['data-epid']
            duration = episode.xpath('.//div[@class="ep-duration"]/span/text()')[0]
            durations = duration.split(":")
            duration_seconds = 0
            for item in durations:
                duration_seconds *= 60
                duration_seconds += int(item)
            date = episode.xpath('.//div[@class="ep-date"]/span/text()')[0]
            match = re.search(r"(\d+).(\d+).(\d+)", date)
            timestamp = time.mktime(datetime.datetime(int(match.group(3)), int(match.group(2)), int(match.group(1))).timetuple())
            tagged_episodes.append(Episode(url, episode_description, title, guid, timestamp, duration_seconds))
        return Show(tagged_episodes, description, title, image_url)

    def get_show_html(self):
        url = 'https://audionow.de/podcast/{}'.format(self.show)
        show_html = util.urlopen(url).read().decode()
        return show_html

    def get_show_metadata(self) -> Show:
        return self.parse_html(self.get_show_html())


def file_metadata(url):
    track_fp = util.urlopen(url)
    headers = track_fp.info()
    filesize = headers['content-length'] or '0'
    filetype = headers['content-type'] or 'application/octet-stream'
    track_fp.close()
    return filesize, filetype


class AudioNowFeed(model.Feed):
    URL_REGEX = re.compile(r'https?://([a-z]+\.)?audionow\.de/podcast/([^/]+)$', re.I)

    @classmethod
    def fetch_channel(cls, channel: PodcastChannel, max_episodes=0):
        url = channel.authenticate_url(channel.url)
        return cls.handle_url(url, max_episodes)

    @classmethod
    def handle_url(cls, url, max_episodes):
        m = cls.URL_REGEX.match(url)
        if m is not None:
            subdomain, showname = m.groups()
            return feedcore.Result(feedcore.UPDATED_FEED, cls(showname, max_episodes))

    def __init__(self, show_name, max_episodes):
        self.show = show_name
        self.metadata = AudioNowShow(show_name).get_show_metadata()
        self.max_episodes = max_episodes

    def get_title(self):
        return self.metadata.title

    def get_cover_url(self):
        return self.metadata.image_url

    def get_link(self):
        return 'https://audionow.de/{}'.format(self.show)

    def get_description(self):
        return self.metadata.description

    def get_new_episodes(self, channel: PodcastChannel, existing_guids: Mapping[str, PodcastEpisode]):
        all_seen_episodes = set()
        all_episodes = []
        for episode in self.metadata.episodes:
            all_seen_episodes.add(episode.guid)
            if episode.guid in existing_guids:
                continue
            episode = channel.episode_factory({
                "description_html": episode.description,
                "description": episode.description,
                "published": episode.date,
                "url": episode.audio_url,
                "guid": episode.guid,
                "title": episode.title,
                "total_time": episode.duration
            })
            all_episodes.append(episode)
        return all_episodes, all_seen_episodes


class gPodderExtension:
    # The extension will be instantiated the first time it's used.
    # You can do some sanity checks here and raise an Exception if
    # you want to prevent the extension from being loaded.
    def __init__(self, container):
        self.container = container

    # This function will be called when the extension is enabled or
    # loaded. This is when you want to create helper objects or hook
    # into various parts of gPodder.
    def on_load(self):
        logger.info('AudioNow Scraper is being loaded.')
        registry.feed_handler.register(AudioNowFeed.fetch_channel)

    # This function will be called when the extension is disabled or
    # when gPodder shuts down. You can use this to destroy/delete any
    # objects that you created in on_load().
    def on_unload(self):
        logger.info('AudioNow Scraper is being unloaded.')
        try:
            registry.feed_handler.unregister(AudioNowFeed.fetch_channel)
        except ValueError:
            pass


    def on_ui_object_available(self, name, ui_object):
        """
        Called by gPodder when ui is ready.
        """
        if name == 'gpodder-gtk':
            self.gpodder = ui_object
