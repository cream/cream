#!/usr/bin/env python

import thread
from urllib import unquote

from cream.contrib.melange import api
from cream.util.subprocess import Subprocess

import dashboard

@api.register('dashboard')
class Dashboard(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.dashboard = dashboard.Dashboard(self.config)

        thread.start_new_thread(self.setup_dashboard, ())

    def setup_dashboard(self):
        self.dashboard.setup()
        self._emit('finished')

        for category in self.dashboard.apps:
            self._emit('add-apps', category)

    @api.in_main_thread
    def _emit(self, signal, *args):
        self.emit(signal, *args)

    @api.expose
    def get_favorites(self):
        return self.dashboard.favorites

    @api.expose
    def update_entries(self):
        self.dashboard.update()

        for category in self.dashboard.apps:
            self._emit('add-apps', category)

    @api.expose
    def add_favorite(self, name):
        self.dashboard.add_favorite(name)

    @api.expose
    def remove_favorite(self, name):
        self.dashboard.remove_favorite(name)

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
