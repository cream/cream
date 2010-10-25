#!/usr/bin/env python

import dbus
import thread
import gobject
gobject.threads_init()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

BUS = dbus.SessionBus()

class Rhythmbox(gobject.GObject):

    __gsignals__ = {
        'song-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'state-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () )

    }

    def __init__(self):
        gobject.GObject.__init__(self)

        self.player = BUS.get_object('org.gnome.Rhythmbox',
                                        '/org/gnome/Rhythmbox/Player')
        self.shell = BUS.get_object('org.gnome.Rhythmbox',
                                        '/org/gnome/Rhythmbox/Shell')

        BUS.add_signal_receiver(self.on_song_changed,
                                dbus_interface='org.gnome.Rhythmbox.Player',
                                signal_name='playingUriChanged')

        BUS.add_signal_receiver(self.on_state_changed,
                                dbus_interface='org.gnome.Rhythmbox.Player',
                                signal_name='playingChanged')

        loop = gobject.MainLoop()
        thread.start_new_thread(loop.run, ())


    def play_pause(self):
        if self.is_playing:
            self.player.playPause(False)
        else:
            self.player.playPause(True)

    def previous(self):
        self.player.previous()

    def next(self):
        self.player.next()

    def set_rating(self, rating):
        uri = self.player.getPlayingUri()
        self.shell.setSongProperty(uri, 'rating', dbus.Double(rating, variant_level=1))

    @property
    def is_playing(self):
        return self.player.getPlaying()

    @property
    def track_data(self):
        uri = self.player.getPlayingUri()
        data = self.shell.getSongProperties(uri)

        artist, album, title, tracknumber, rating, duration = \
            map(lambda key: data.get(key, None),
                ('artist', 'album', 'title', 'track-number', 'rating', 'duration'))

        return dict(artist=artist,
                    album=album,
                    title=title,
                    tracknumber=tracknumber,
                    rating=rating,
                    duration=duration
        )

    def on_song_changed(self, uri):
        self.emit('song-changed')

    def on_state_changed(self, state):
        self.emit('state-changed')


if __name__ == '__main__':
    box = Rhythmbox()
