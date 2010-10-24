#!/usr/bin/env python

try:
    import cPickle as pickle
except:
    import pickle

from os.path import join

from cream.contrib.melange import api
from cream.util.subprocess import Subprocess
from cream.contrib.desktopentries import DesktopEntry

from cream.util.string import crop_string
from util import icon_to_base64
from urllib import unquote

@api.register('dashboard')
class Dashboard(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.entries = [entry for entry in DesktopEntry.get_all() if hasattr(entry, 'icon')]

    @api.expose
    def get_all_apps(self):
        apps = []
        for entry in self.entries:
            base64 = icon_to_base64(entry.icon)
            if not base64:
                # no icon
                continue
            app = {}
            app['name'] = crop_string(entry.name, 8, '..')
            app['cmd'] = self.parse_cmd(entry.exec_)
            app['icon'] = base64
            apps.append(app)
        return apps

    @api.expose
    def launch_app(self, cmd, arg):
        cmd = cmd.strip()
        cmd = str(cmd).split()

        if arg:
            cmd += [self.parse_arg(arg)]

        Subprocess(cmd).run()

    def parse_cmd(self, cmd):
        cmd = cmd.replace('%F', '')
        cmd = cmd.replace('%f', '')
        cmd = cmd.replace('%U', '')
        cmd = cmd.replace('%u', '')
        return cmd

    def parse_arg(self, arg):
        arg = str(arg)
        arg = unquote(arg)
        if arg.startswith('file://'):
            return arg.replace('file://', '')
        return ''
