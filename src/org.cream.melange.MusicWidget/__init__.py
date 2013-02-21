#!/usr/bin/env python

import os
from PIL import Image
from melange import api
from dbus import DBusException

# initialize lxml
import lxml.etree
lxml.etree.set_default_parser(lxml.etree.XMLParser(no_network=False))

from coverart import get_cover, config
from player import Player, NoMprisPlayerFound


COVERART_SIZE = 150,150

def resize(path):
    image = Image.open(path)
    if not image.size == COVERART_SIZE:
        image.thumbnail(COVERART_SIZE, Image.ANTIALIAS)
        image.save(path, image.format)
    return path


def connect_to_player_if_necessary(func):

    def wrapper(self, *args):
        if self.player is None:
            try:
                self.player = Player()
                self.connect_signals()
                self.emit('player-connected')
            except NoMprisPlayerFound:
                pass

        return func(self, *args)

    return wrapper


def handle_dbus_exceptions(func):

    def wrapper(self, *args):
        if self.player is not None:
            try:
                return func(self, *args)
            except DBusException:
                self.player = None
                self.emit('player-disconnected')

    return wrapper


@api.register('org.cream.melange.MusicWidget')
class Music(api.API):

    def __init__(self):
        api.API.__init__(self)

        config.COVER_ART_BASE_DIR = os.path.join(self.get_data_path(), 'coverart')
        if not os.path.exists(config.COVER_ART_BASE_DIR):
            os.mkdir(config.COVER_ART_BASE_DIR)

        try:
            self.player = Player()
        except NoMprisPlayerFound:
            self.player = None

        self.connect_signals()

    def connect_signals(self):
        if self.player is not None:
            self.player.connect('song-changed',
                lambda p, song: self.emit('song-changed', song)
            )
            self.player.connect('state-changed',
                lambda p, state: self.emit('state-changed', state)
            )

    @api.expose
    @api.in_main_thread
    @connect_to_player_if_necessary
    @handle_dbus_exceptions
    def previous(self):
        self.player.previous()


    @api.expose
    @api.in_main_thread
    @connect_to_player_if_necessary
    @handle_dbus_exceptions
    def next(self):
        self.player.next()


    @api.expose
    @api.in_main_thread
    @connect_to_player_if_necessary
    @handle_dbus_exceptions
    def play_pause(self):
        self.player.play_pause()


    @api.expose
    @api.in_main_thread
    @connect_to_player_if_necessary
    @handle_dbus_exceptions
    def is_playing(self):
        return self.player.is_playing

    @api.expose
    @api.in_main_thread
    @connect_to_player_if_necessary
    @handle_dbus_exceptions
    def get_data(self):
        return self.player.current_track

    @api.expose
    @api.in_main_thread
    @connect_to_player_if_necessary
    @handle_dbus_exceptions
    def get_coverart(self):
        track = self.player.current_track
        artist, album = track.get('artist'), track.get('album')
        if artist is None or album is None:
            return None
        path = get_cover(artist, album)
        resize(path)
        return os.path.split(path)[1]
