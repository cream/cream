#!/usr/bin/env python

try:
    import cPickle as pickle
except:
    import pickle

from os.path import join

from cream.contrib.melange import api
from cream.util.subprocess import Subprocess
from cream.contrib.desktopentries import DesktopEntry

from util import icon_to_base64

@api.register('dashboard')
class Dashboard(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.dump_file = join(self.context.working_directory, 'favourites.dump')

        self.entries = [entry for entry in DesktopEntry.get_all() if hasattr(entry, 'icon')]
        self.favourites = []#self.load()


    def load(self):
        with open(self.dump_file, 'r') as f:
            return pickle.load(f)

    def save(self):
        with open(self.dump_file, 'w') as f:
            pickle.dump(self.favourites, f)


    @api.expose
    def get_all_apps(self):
        apps = []
        for entry in self.entries:
            app = {}
            app['name'] = entry.name
            app['cmd'] = entry.exec_
            base64 = icon_to_base64(entry.icon)
            if base64:
                app['icon'] = base64

            apps.append(app)

        return apps

    @api.expose
    def launch_app(self, cmd):
        Subprocess(str(cmd).split()).run()
