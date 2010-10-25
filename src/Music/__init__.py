#!/usr/bin/env python

import os.path
from PIL import Image
from cream.contrib.melange import api

from players import Rhythmbox
from libcoverart import get_cover
from libcoverart import config

import lxml.etree
lxml.etree.set_default_parser(lxml.etree.XMLParser(no_network=False))


size = 150,150

def resize(path):
    image = Image.open(path)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(path, image.format)
    return path

@api.register('music')
class Music(api.API):

    def __init__(self):
        api.API.__init__(self)
        config.COVER_ART_BASE_DIR = os.path.join(self.context.working_directory,
                                                'skins/default/coverart')

        self.player = Rhythmbox()

        self.player.connect('song-changed', self.song_changed)
        self.player.connect('state-changed', self.state_changed)

    def song_changed(self, player):
        self.emit('song-changed')

    def state_changed(self, player):
        self.emit('state-changed')

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
            return self.player.track_data
        return _get_data()

    @api.expose
    def get_coverart(self):
        @api.in_main_thread
        def _get_coverart():
            track = self.player.track_data
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
