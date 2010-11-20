#!/usr/bin/env python

import gobject
gobject.threads_init()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import thread

class BasePlayerController(gobject.GObject):

    __gsignals__ = {
        'song-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'state-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () )
    }

    def __init__(self):
        gobject.GObject.__init__(self)

        self.loop = gobject.MainLoop()
        thread.start_new_thread(self.run, ())

    def run(self):
        self.loop.run()

    def quit(self):
        raise NotImplementedError

    def play_pause(self):
        raise NotImplementedError

    def previous(self):
        raise NotImplementedError

    def next(self):
        raise NotImplementedError

    def set_rating(self, rating):
        raise NotImplementedError

    @property
    def is_playing(self):
        raise NotImplementedError

    @property
    def current_track(self):
        raise NotImplementedError

    def on_song_changed(self, *args):
        self.emit('song-changed')

    def on_state_changed(self, *args):
        self.emit('state-changed')
