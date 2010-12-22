#!/usr/bin/env python

import thread
from urllib import unquote

from melange import api
from cream.util.subprocess import Subprocess

import dashboard

@api.register('dashboard')
class Dashboard(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.dashboard = dashboard.Dashboard(self.config, self.get_data_path())
        self.dashboard.connect('load-apps', lambda s, apps: self._emit('load-apps', apps))
        self.dashboard.connect('load-favorites', lambda s, apps: self._emit('load-favorites', apps))

        thread.start_new_thread(self.dashboard.setup, ())


    @api.in_main_thread
    def _emit(self, signal, *args):
        self.emit(signal, *args)

    @api.expose
    def update_entries(self):
        self.dashboard.update()

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

        @api.in_main_thread
        def _launch_app():
            Subprocess(cmd, fork=True).run()
        _launch_app()

    def parse_arg(self, arg):
        arg = str(arg)
        arg = unquote(arg)
        if arg.startswith('file://'):
            return arg.replace('file://', '')
        return ''
