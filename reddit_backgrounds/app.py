
import configparser
import random

from abc import abstractmethod, ABCMeta
from typing import Iterable
from itertools import islice
from pathlib import Path

import appdirs
import praw
from praw.objects import Submission
import requests

from .globals import *
from .utils import get_desktop_environment


class BackgroundApp(metaclass=ABCMeta):
    def __init__(self):
        app_folder = Path(appdirs.user_data_dir(APP_ID))
        config_folder = Path(appdirs.user_config_dir(APP_ID))

        for folder in app_folder, config_folder:
            if not folder.is_dir():
                folder.mkdir(parents=True)

        self.config_file = Path(config_folder) / CONFIG_FILE
        self.config = configparser.ConfigParser()
        self.settings = None
        self.load_settings()

        self.background_dest = app_folder / BACKGROUND_FILENAME

    def load_settings(self):
        self.config = configparser.ConfigParser()
        if self.config_file.is_file():
            with self.config_file.open() as f:
                self.config.read_file(f)
        if not self.config.has_section(CONFIG_SECTION):
            self.config.add_section(CONFIG_SECTION)
        self.settings = self.config[CONFIG_SECTION]
        self.save_settings()

    def save_settings(self):
        with self.config_file.open('w') as f:
            self.config.write(f)

    def next_background(self):
        try:
            self._try_next_background()
        except Exception as e:
            self.show_notification('Background error', str(e))

    @abstractmethod
    def _try_next_background(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def update_background(self):
        pass

    @abstractmethod
    def show_notification(self, title: str, text: str):
        pass

    def quit(self):
        return


class RedditBackgroundApp(BackgroundApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.reddit = praw.Reddit(user_agent=USER_AGENT)

    @staticmethod
    def filter_pictures(subs: Iterable[Submission]) -> Iterable[Submission]:
        # Could do a head request, but that's slower
        for sub in subs:
            if sub.url.split('.')[-1].lower() not in ('png', 'jpg', 'jpeg', 'gif'):
                continue
            yield sub

    def _try_next_background(self):
        sub_name = self.settings.get('subreddit', 'EarthPorn')
        count = self.settings.getint('post_count', 10)
        print('Locating image')
        image = random.choice(list(islice(self.filter_pictures(
            self.reddit.get_subreddit(sub_name).get_top_from_day()),
            count)))
        print('Downloading', image.url)
        r = requests.get(image.url)
        if not r.ok:
            raise IOError('Could not get image')
        if not r.headers['Content-Type'].split('/')[0] == 'image':
            raise IOError('URL is not image')
        with self.background_dest.open('wb') as f:
            f.write(r.content)
        self.update_background()
        self.show_notification(
            'Picture from ' + image.subreddit.url,
            image.title)


def get_app() -> BackgroundApp:
    desktop = get_desktop_environment()
    if desktop in ('gnome', 'unity', 'cinnamon', 'x-cinnamon'):
        from .gtk.app import GnomeBackgroundApp
        return GnomeBackgroundApp
    elif desktop == 'mate':
        from .gtk.app import MateBackgroundApp
        return MateBackgroundApp
    raise NotImplementedError(
        'The desktop environment %s is not currently supported' % desktop)
