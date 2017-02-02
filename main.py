#!/usr/bin/env python3

import random
import signal
import os
from typing import Iterable, Callable
from itertools import islice

import appdirs
import praw
import requests

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import AppIndicator3
from gi.repository import Notify

APP_ID = 'reddit-backgrounds'
SUBREDDIT = 'earthporn'
COUNT = 10


def add_menu(menu: Gtk.Menu, title: str, func: Callable, event: str='activate'):
    item = Gtk.MenuItem(title)
    item.connect(event, func)
    menu.append(item)
    return item


def enum_pics(subs: Iterable[praw.objects.Submission]):
    # Could do a head request, but that's slower
    for sub in subs:
        if sub.url.split('.')[-1].lower() not in ('png', 'jpg', 'jpeg', 'gif'):
            continue
        yield sub


class RedditBackgroundApp:
    def __init__(self):
        icon_theme = Gtk.IconTheme.get_default()
        self.indicator = AppIndicator3.Indicator.new(
            APP_ID,
            icon_theme.lookup_icon('preferences-desktop-wallpaper', 16, 0).get_filename(),
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)

        app_folder = appdirs.user_data_dir(APP_ID)
        if not os.path.isdir(app_folder):
            os.makedirs(app_folder)

        self.reddit = praw.Reddit(user_agent='reddit-backgrounds')
        self.background_dest = os.path.join(app_folder, 'current-background')

        self.gsettings = Gio.Settings.new('org.gnome.desktop.background')

        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())
        Notify.init(APP_ID)

    def build_menu(self):
        menu = Gtk.Menu()

        add_menu(menu, 'Next Background', self.next_background)
        add_menu(menu, 'Quit', self.quit)

        menu.show_all()
        return menu

    def _try_next_background(self):
        print('Locating image')
        image = random.choice(list(islice(enum_pics(
            self.reddit.get_subreddit(SUBREDDIT).get_top_from_day()),
            COUNT)))
        print('Downloading', image.url)
        r = requests.get(image.url)
        if not r.ok:
            raise IOError('Could not get image')
        if not r.headers['Content-Type'].split('/')[0] == 'image':
            raise IOError('URL is not image')
        with open(self.background_dest, 'wb') as f:
            f.write(r.content)
        self.gsettings.set_string(
            'picture-uri',
            "file://" + self.background_dest)
        note = Notify.Notification()
        note.update(
            'Picture from ' + image.subreddit.url,
            image.title)
        note.show()

    def next_background(self, source):
        try:
            self._try_next_background()
        except Exception as e:
            error = Notify.Notification()
            error.update('Reddit error', str(e))
            error.show()

    def quit(self, source):
        Notify.uninit()
        Gtk.main_quit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = RedditBackgroundApp()
    Gtk.main()
