#!/usr/bin/env python

from urllib import unquote

from cream.contrib.melange import api
from cream.util.subprocess import Subprocess

import dashboard

@api.register('dashboard')
class Dashboard(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.dashboard = dashboard.Dashboard(self.config)

    @api.expose
    def get_all_apps(self):
        return self.dashboard.get_apps()

    @api.expose
    def get_favorites(self):
        return self.dashboard.get_favorites()

    @api.expose
    def update_entries(self):
        self.apps = self.dashboard.update()

    @api.expose
    def add_favorite(self, name):
        @api.in_main_thread
        def _add_favorite():
            self.dashboard.add_favorite(name)
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
