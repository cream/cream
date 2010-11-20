#!/usr/bin/env python

import os
from PIL import Image
from cream.contrib.melange import api

import players
from coverart import get_cover, config

import lxml.etree
lxml.etree.set_default_parser(lxml.etree.XMLParser(no_network=False))

PLAYERS = {
    'banshee': players.Banshee,
    'rhythmbox': players.Rhythmbox
}


COVERART_SIZE = 150,150

def resize(path):
    image = Image.open(path)
    image.thumbnail(COVERART_SIZE, Image.ANTIALIAS)
    image.save(path, image.format)
    return path

@api.register('music')
class Music(api.API):

    def __init__(self):
        api.API.__init__(self)
        config.COVER_ART_BASE_DIR = os.path.join(self.context.working_directory,
                                                'skins/default/coverart')

        self.player = PLAYERS[self.config.player]()

        self.player.connect('song-changed', self.song_changed)
        self.player.connect('state-changed', self.state_changed)

    def song_changed(self, player):
        self.emit('song-changed')

    def state_changed(self, player):
        self.emit('state-changed')

    @api.expose
    def change_player(self):
        @api.in_main_thread
        def _change_player():
            self.player.quit()
            self.player = PLAYERS[self.config.player]()
            self.player.connect('song-changed', self.song_changed)
            self.player.connect('state-changed', self.state_changed)
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
