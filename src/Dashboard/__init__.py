#!/usr/bin/env python

from os.path import join

from cream.contrib.melange import api
from cream.util.subprocess import Subprocess
from cream.contrib.desktopentries import DesktopEntry
from cream.contrib.desktopentries import DEFAULT_CATEGORIES

from cream.util.string import crop_string
from cream.util.dicts import ordereddict
from util import icon_to_base64, parse_cmd
from urllib import unquote

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
        app['category'] = entry.recommended_category
        return app

@api.register('dashboard')
class Dashboard(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.entries = []
        entries = ordereddict()
        for category in sorted(DEFAULT_CATEGORIES):
            if getattr(self.config, category, False):
                entries[category] = []
        for entry in DesktopEntry.get_all():
            if not hasattr(entry, 'icon'):
                continue
            app = App.from_entry(entry)
            if app is None or app['category'] is None:
                continue

            if app['category'] in entries:
                entries[app['category']].append(app)

        for category in entries.itervalues():
            if not category:
                continue
            self.entries.append(sorted(category, key=lambda app: app['name'].lower()))

    @api.expose
    def get_all_apps(self):
        return self.entries


    @api.expose
    def launch_app(self, cmd, arg):
        cmd = cmd.strip()
        cmd = str(cmd).split()

        if arg:
            cmd += [self.parse_arg(arg)]

        Subprocess(cmd).run()


    def parse_arg(self, arg):
        arg = str(arg)
        arg = unquote(arg)
        if arg.startswith('file://'):
            return arg.replace('file://', '')
        return ''
