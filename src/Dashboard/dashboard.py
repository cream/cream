#!/usr/bin/env python

import gobject

from cream.util.dicts import ordereddict
from cream.contrib.desktopentries import DesktopEntry

from util import CATEGORIES, app_from_entry


class Dashboard(gobject.GObject):
    __gsignals__ = {
        'load-apps': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'load-favorites': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    def __init__(self, config, icon_path):
        gobject.GObject.__init__(self)

        self.config = config
        self.icon_path = icon_path

    def setup(self):
        self.apps = self._parse_apps_from_entries()
        self.favorites = self._parse_favorites_from_config()

    def update(self):
        self.apps = self._parse_apps_from_entries()

    def add_favorite(self, name):
        self.config.favorites.append(name)
        self.config.save()

    def remove_favorite(self, name):
        self.config.favorites.remove(name)
        self.config.save()

    def _parse_apps_from_entries(self):
        categories = self._get_categories_from_config()

        for entry in DesktopEntry.get_all():
            app = app_from_entry(entry, self.icon_path)
            if app is None or app['category'] is None:
                continue
            elif app['category'] in categories:
                categories[app['category']].append(app)

        apps = []
        for category in categories.itervalues():
            if category:
                sorted_category = sorted(category, key=lambda app: app['name'].lower())
                self.emit('load-apps', sorted_category)
                apps.append(sorted_category)
        return apps

    def _get_categories_from_config(self):
        categories = ordereddict()
        for category in sorted(CATEGORIES.values()):
            if getattr(self.config, category, False):
                categories[category] = []
        return categories


    def _parse_favorites_from_config(self):
        favorites = list(self.config.favorites)

        for entry in DesktopEntry.get_all():
            if entry.name in favorites:
                app = app_from_entry(entry, self.icon_path)
                index = favorites.index(entry.name)
                favorites[index] = app
        self.emit('load-favorites', favorites)
        return favorites
