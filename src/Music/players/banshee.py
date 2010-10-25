#!/usr/bin/env python

import dbus
import thread
import gobject


class Banshee(gobject.GObject):


    def __init__(self):
        gobject.GObject.__init__(self)

    def _connect_to_signa
