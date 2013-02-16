#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from melange import api

import pasty
from gi.repository import Gtk as gtk, Gdk as gdk


@api.register('org.cream.melange.PasteWidget')
class Paste(api.API):

    def __init__(self):

        api.API.__init__(self)

        self.language = pasty.dpaste.default_language
        self.clipboard = gtk.Clipboard.get(gdk.SELECTION_CLIPBOARD)


    @api.expose
    def get_languages(self):
        return pasty.dpaste.languages


    @api.expose
    def set_language(self, lang):
        self.language = lang

    @api.expose
    def paste_clipboard(self):

        text = self.get_clipboard()
        url = self.paste(text, self.language)
        return url


    @api.expose
    def paste_file(self):

        text = self.get_file()
        url = self.paste(text, self.language)
        return url


    @api.expose
    def paste_file_from_uri(self, uri):

        path = uri.replace('file://', '')
        path = path.replace('%20', ' ')

        with open(path) as fh:
            text = fh.read()

        url = self.paste(text, self.language)
        return url


    @api.in_main_thread
    def get_clipboard(self):
        return self.clipboard.wait_for_text()


    @api.in_main_thread
    def get_file(self):

        chooser = gtk.FileChooserDialog(buttons=(
            gtk.STOCK_CANCEL, 
            gtk.ResponseType.REJECT,
            gtk.STOCK_OK, 
            gtk.ResponseType.ACCEPT))
        response = chooser.run()
        if response == gtk.ResponseType.ACCEPT:
            with open(chooser.get_filename()) as fh:
                text = fh.read()
            response = chooser.destroy()
            return text
        elif response == gtk.ResponseType.REJECT:
            response = chooser.destroy()
        return None


    def paste(self, text, language):
        return pasty.dpaste.do_paste(text, language)
