#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cream.ipc
from cream.contrib.melange import api

@api.register('thingy')
class ThingyArea(api.API):

    def __init__(self):
        api.API.__init__(self)
        self.melange = cream.ipc.get_object('org.cream.Melange', '/org/cream/Melange')
        
    @api.expose
    def toggle_overlay(self):
        self._toggle()
        
        
    @api.in_main_thread
    def _toggle(self):
        self.melange.toggle_overlay()
