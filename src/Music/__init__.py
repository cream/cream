#!/usr/bin/env python

import os
from PIL import Image
from cream.contrib.melange import api

# initialize lxml
import lxml.etree
lxml.etree.set_default_parser(lxml.etree.XMLParser(no_network=False))

from coverart import get_cover, config
import players

PLAYERS = {
    'banshee': players.Banshee,
    'rhythmbox': players.Rhythmbox
}


COVERART_SIZE = 150,150

def resize(path):
    image = Image.open(path)
    if not image.size == COVERART_SIZE:
        image.thumbnail(COVERART_SIZE, Image.ANTIALIAS)
        image.save(path, image.format)
    return path

@api.register('music')
class Music(api.API):

    def __init__(self):
        api.API.__init__(self)

        config.COVER_ART_BASE_DIR = os.path.join(self.get_data_path(), 'coverart')
        if not os.path.exists(config.COVER_ART_BASE_DIR):
            os.mkdir(config.COVER_ART_BASE_DIR)

        self.player = PLAYERS[self.config.player]()

        self.player.connect('song-changed', lambda p, song: self.emit('song-changed', song))
        self.player.connect('state-changed', lambda p, state: self.emit('state-changed', state))

    @api.expose
    def change_player(self):
        @api.in_main_thread
        def _change_player():
            self.player.quit()
            self.player = PLAYERS[self.config.player]()
            self.player.connect('song-changed', lambda p, song: self.emit('song-changed', song))
            self.player.connect('state-changed', lambda p, state: self.emit('state-changed', state))
        _change_player()

    @api.expose
    def previous(self):
        @api.in_main_thread
        def _previous():
            self.player.previous()
        _previous()

    @api.expose
    def next(self):
        @api.in_main_thread
        def _next():
            self.player.next()
        _next()

    @api.expose
    def play_pause(self):
        @api.in_main_thread
        def _play_pause():
            self.player.play_pause()
        _play_pause()

    @api.expose
    def is_playing(self):
        @api.in_main_thread
        def _is_playing():
            return self.player.is_playing
        return _is_playing()

    @api.expose
    def get_data(self):
        @api.in_main_thread
        def _get_data():
            return self.player.current_track
        return _get_data()

    @api.expose
    def get_coverart(self):
        @api.in_main_thread
        def _get_coverart():
            track = self.player.current_track
            artist, album = track.get('artist'), track.get('album')
            if artist is None or album is None:
                return None
            path = get_cover(track.get('artist'), track.get('album'))
            resize(path)
            return os.path.split(path)[1]
        return _get_coverart()

    @api.expose
    def set_rating(self, rating):
        @api.in_main_thread
        def _set_rating():
            self.player.set_rating(rating)
        _set_rating()
