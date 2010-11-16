#!/usr/bin/env python

from cream.contrib.desktopentries import DesktopEntry

from cream.util.string import crop_string
from cream.util.dicts import ordereddict

from util import icon_to_base64, parse_cmd


CATEGORIES = {'Development': 'Development',
              'AudioVideo': 'Multimedia',
              'Network': 'Network',
              'Office': 'Office',
              'Settings': 'Settings',
              'System': 'System',
              'Game': 'Games',
              'Graphics': 'Graphics',
              'Utility': 'Utility'
}

def app_from_entry(entry):
    if not hasattr(entry, 'icon'):
        return None
    base64 = icon_to_base64(entry.icon)
    if not base64:
        return None

    app = {}
    app['name'] = entry.name
    app['label'] = crop_string(entry.name, 8, '..')
    app['cmd'] = parse_cmd(entry.exec_)
    app['icon'] = base64
    app['category'] = CATEGORIES.get(entry.recommended_category, '')
    return app


class Dashboard(object):

    def __init__(self, config):
        self.config = config


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
            app = app_from_entry(entry)
            if app is None or app['category'] is None:
                continue
            elif app['category'] in categories:
                categories[app['category']].append(app)

        apps = []
        for category in categories.itervalues():
            if category:
                apps.append(sorted(category, key=lambda app: app['name'].lower()))
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
                app = app_from_entry(entry)
                index = favorites.index(entry.name)
                favorites[index] = app
        return favorites
