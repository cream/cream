#!/usr/bin/env python

from urllib import unquote

from cream.contrib.melange import api
from cream.util.subprocess import Subprocess
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
class App(object):

    @classmethod
    def from_entry(cls, entry):
        app = {}
        base64 = icon_to_base64(entry.icon)
        if not base64:
            return None
        app['name'] = crop_string(entry.name, 8, '..')
        app['cmd'] = parse_cmd(entry.exec_)
        app['icon'] = base64
        app['category'] = CATEGORIES.get(entry.recommended_category, '')
        return app

@api.register('dashboard')
class Dashboard(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.favorites = self.load_favorites()
        self.entries = self.get_entries()

    def get_entries(self):
        entries = ordereddict()
        for category in sorted(CATEGORIES.values()):
            if getattr(self.config, category, False):
                entries[category] = []
        for entry in DesktopEntry.get_all():
            if not hasattr(entry, 'icon'):
                continue

            app = App.from_entry(entry)
            if app is None or app['category'] is None:
                continue

            elif app['category'] in entries:
                entries[app['category']].append(app)

                if app['name'] in self.favorites:
                    index = self.favorites.index(app['name'])
                    self.favorites[index] = app

        e = []
        for category in entries.itervalues():
            if not category:
                continue
            e.append(sorted(category, key=lambda app: app['name'].lower()))
        return e

    def load_favorites(self):
        favorites = self.config.favorites
        if favorites == 'None':
            return []
        return favorites.split('\n')

    @api.expose
    def get_all_apps(self):
        return self.entries

    @api.expose
    def get_favorites(self):
        return self.favorites

    @api.expose
    def update_entries(self):
        self.entries = self.get_entries()

    @api.expose
    def add_favorite(self, name):
        @api.in_main_thread
        def _add_favorite():
            favorites = self.config.favorites
            if favorites == 'None':
                self.config.favorites = name
            else:
                self.config.favorites += '\n' + name
        _add_favorite()

    @api.expose
    def launch_app(self, cmd, arg):
        cmd = cmd.strip()
        cmd = str(cmd).split()

        if arg:
            cmd += [self.parse_arg(arg)]

        Subprocess(cmd, fork=True).run()


    def parse_arg(self, arg):
        arg = str(arg)
        arg = unquote(arg)
        if arg.startswith('file://'):
            return arg.replace('file://', '')
        return ''
