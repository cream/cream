#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

import gobject

from cream.contrib.melange import api
from cream.contrib.desktopentries import DesktopEntry, gtkmenu

@api.register('appmenu')
class AppMenu(api.API):

    def __init__(self):
        api.API.__init__(self)
        self.menu = gtkmenu.to_gtk(DesktopEntry.get_all())

    @api.in_main_thread
    def _show_menu(self):

        self.menu.popup(None, None, None, 1, 0)

    @api.expose
    def show_menu(self):

        self._show_menu()

