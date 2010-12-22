#!/usr/bin/env python

import dbus
BUS = dbus.SessionBus()

from players.base import BasePlayerController

class Banshee(BasePlayerController):

    def __init__(self):
        self.player_engine = BUS.get_object('org.bansheeproject.Banshee',
                                '/org/bansheeproject/Banshee/PlayerEngine')
        self.playback_controller = BUS.get_object('org.bansheeproject.Banshee',
                            '/org/bansheeproject/Banshee/PlaybackController')

        BUS.add_signal_receiver(self.state_changed,
            dbus_interface="org.bansheeproject.Banshee.PlayerEngine",
            signal_name="StateChanged"
        )
        BUS.add_signal_receiver(self.state_changed,
            dbus_interface="org.bansheeproject.Banshee.PlayerEngine",
            signal_name="EventChanged"
        )

        BasePlayerController.__init__(self)

    def quit(self):
        BUS.remove_signal_receiver(self.state_changed, signal_name='StateChanged')
        BUS.remove_signal_receiver(self.state_changed, signal_name='EventChanged')

    def state_changed(self, state, *args):
        if state in ('paused', 'playing'):
            self.on_state_changed(state)
        elif state in ('startofstream'):
            self.on_song_changed(self.current_track)

    def play_pause(self):
        self.player_engine.TogglePlaying()

    def previous(self):
        self.playback_controller.Previous(False)

    def next(self):
        self.playback_controller.Next(False)

    def set_rating(self, rating):
        self.player_engine.SetRating(dbus.Byte(int(rating)))

    @property
    def is_playing(self):
        if str(self.player_engine.GetCurrentState()) == 'playing':
            return True
        else:
            return False

    @property
    def current_track(self):
        track = self.player_engine.GetCurrentTrack()

        artist, album, title, tracknumber, duration = \
            map(lambda key: track.get(key, None),
                ('artist', 'album', 'name', 'track-number', 'length'))

        rating = int(self.player_engine.GetRating())
        position = self.current_position
        return {'artist': artist,
                'album': album,
                'title': title,
                'tracknumber': tracknumber,
                'rating': rating,
                'duration': duration,
                'position': position
        }

    @property
    def current_position(self):
        position = self.player_engine.GetPosition()
        return float(position / 1000)
