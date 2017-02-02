
import signal
from typing import Callable

from ..app import RedditBackgroundApp
from ..globals import APP_ID

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import AppIndicator3
from gi.repository import Notify


def add_menu(menu: Gtk.Menu, title: str, func: Callable, event: str='activate'):
    item = Gtk.MenuItem(title)
    item.connect(event, func)
    menu.append(item)
    return item


class GtkBackgroundApp(RedditBackgroundApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        icon = self.settings.get('icon', 'preferences-desktop-wallpaper')
        if not icon.startswith('/'):
            theme_icon = Gtk.IconTheme.get_default().lookup_icon(icon, 16, 0)
            if theme_icon is None:
                raise ValueError('An icon named %s could not be found in the theme' % icon)
            icon = theme_icon.get_filename()

        self.indicator = AppIndicator3.Indicator.new(
            APP_ID, icon,
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)

        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())
        Notify.init(APP_ID)

    def build_menu(self):
        menu = Gtk.Menu()

        add_menu(menu, 'Next Background', lambda _: self.next_background())
        add_menu(menu, 'Quit', lambda _: self.quit())

        menu.show_all()
        return menu

    def start(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()

    def show_notification(self, title: str, text: str):
        note = Notify.Notification()
        note.update(title, text)
        note.show()

    def quit(self):
        super().quit()
        Notify.uninit()
        Gtk.main_quit()


class GnomeBackgroundApp(GtkBackgroundApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gsettings = Gio.Settings.new('org.gnome.desktop.background')

    def update_background(self):
        self.gsettings.set_string('picture-uri', self.background_dest.as_uri())


# Untested, see http://wiki.mate-desktop.org/docs:gsettings
class MateBackgroundApp(GtkBackgroundApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gsettings = Gio.Settings.new('org.mate.background')

    def update_background(self):
        self.gsettings.set_string('picture-filename', str(self.background_dest))

# TODO: Plasma Desktop (KDE 5)
