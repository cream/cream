#!/usr/bin/env python

import dbus
BUS = dbus.SessionBus()

from players.base import BasePlayerController

class Rhythmbox(BasePlayerController):

    def __init__(self):

        self.player = BUS.get_object('org.gnome.Rhythmbox',
                                      '/org/gnome/Rhythmbox/Player')
        self.shell = BUS.get_object('org.gnome.Rhythmbox',
                                     '/org/gnome/Rhythmbox/Shell')

        BUS.add_signal_receiver(self.song_changed,
                                dbus_interface='org.gnome.Rhythmbox.Player',
                                signal_name='playingUriChanged')
        BUS.add_signal_receiver(self.state_changed,
                                dbus_interface='org.gnome.Rhythmbox.Player',
                                signal_name='playingChanged')

        BasePlayerController.__init__(self)


    def quit(self):
        BUS.remove_signal_receiver(self.on_song_changed)
        BUS.remove_signal_receiver(self.on_state_changed)

    def song_changed(self, *args):
        self.on_song_changed(self.current_track)

    def state_changed(self, state):
        if state:
            self.on_state_changed('playing')
        else:
            self.on_state_changed('paused')

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
    def current_track(self):
        uri = self.player.getPlayingUri()
        track = self.shell.getSongProperties(uri)

        artist, album, title, tracknumber, rating, duration = \
            map(lambda key: track.get(key, None),
                ('artist', 'album', 'title', 'track-number', 'rating', 'duration'))

        return {'artist': artist,
                'album': album,
                'title': title,
                'tracknumber': tracknumber,
                'rating': rating,
                'duration': duration
        }
