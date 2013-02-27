from gi.repository import GObject as gobject

import dbus
import cream.ipc


def clean_metadata(metadata):
    return {
        'artist': unicode(metadata['xesam:artist'][0]),
        'album': unicode(metadata['xesam:album']),
        'title': unicode(metadata['xesam:title']),
        'tracknumber': int(metadata['xesam:trackNumber']),
        'rating': int(metadata.get('xesam:userRating', 0) * 5),
        'duration': int(metadata['mpris:length']) / 1000000
    }


class NoMprisPlayerFound(Exception): pass

class Player(gobject.GObject):
    mpris_interface = 'org.mpris.MediaPlayer2.Player'

    __gsignals__ = {
        'song-changed': (gobject.SignalFlags.RUN_LAST, None, (object,)),
        'state-changed': (gobject.SignalFlags.RUN_LAST, None, (object,))
    }

    def __init__(self):
        gobject.GObject.__init__(self)

        # find a player
        player = None
        for name in cream.ipc.SESSION_BUS.list_names():
            if 'org.mpris.MediaPlayer2' in name:
                player = name
                break

        if player is None:
            raise NoMprisPlayerFound()

        proxy = cream.ipc.SESSION_BUS.get_object(player, '/org/mpris/MediaPlayer2')
        self._player = dbus.Interface(proxy, 'org.mpris.MediaPlayer2.Player')
        self._player_properties = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')

        self._player_properties.connect_to_signal('PropertiesChanged', self.on_property_change)

    def _set_property(self, name, value):
        self._player_properties.Set(self.mpris_interface, name ,value)

    def _get_property(self, name):
        return self._player_properties.Get(self.mpris_interface, name)

    def on_property_change(self, interface, data, *args):

        if 'Metadata' in data:
            self.emit('song-changed', self.current_track)
        elif 'PlaybackStatus' in data:
            self.emit('state-changed', self.current_state)

    def play_pause(self):
        self._player.PlayPause()

    def previous(self):
        self._player.Previous()

    def next(self):
        self._player.Next()

    @property
    def current_position(self):
        return self._get_property('Position') / 1000000

    @property
    def current_state(self):
        return {
            'Playing': 'playing',
            'Paused': 'paused',
            'Stopped': 'stopped'
        }[self._get_property('PlaybackStatus')]

    @property
    def is_playing(self):
        return self.current_state == 'playing'

    @property
    def current_track(self):
        track = clean_metadata(self._get_property('Metadata'))
        track['position'] = self.current_position
        return track

