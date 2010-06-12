#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import gtk
import gobject

from cream.contrib.melange import api
from cream.contrib.appindicators.host import StatusNotifierHost, Status

def construct_js_item(item, icon_filename):
    return {
        'icon': icon_filename,
        'id': item.id,
    }

@api.register('appindicators')
class AppIndicators(api.API):

    def __init__(self):
        api.API.__init__(self)

        # Intialize the DBus stuff here...
        self.host = StatusNotifierHost()
        self.host.connect('item-added', self.sig_item_added)
        self.host.connect('item-removed', self.sig_item_removed)

        self.add_initially()

    def store_icon(self, item, filename):
        pb = gtk.gdk.pixbuf_new_from_file(filename)
        data = StringIO()
        def _callback(buf):
            data.write(buf)
        pb.save_to_callback(_callback, 'png')
        base64 = data.getvalue().encode('base64')
        return base64

    def store_current_icon(self, item):
        return self.store_icon(item, item.get_current_icon_filename())

    def change_item(self, item):
        self.emit('item-changed', construct_js_item(item, self.store_current_icon(item)))

    def sig_item_added(self, host, item):
        self.emit('item-added', construct_js_item(item, self.store_current_icon(item)))
        item.connect('status-new', self.sig_status_new)

    def sig_status_new(self, item, status):
        self.change_item(item)

    def sig_item_removed(self, host, item):
        self.emit('item-removed', item.id)

    def add_initially(self):
        for item in self.host.items:
            self.sig_item_added(self.host, item)

    @api.expose
    def get_items(self):

        items = []

        for item in self.host.items:
            items.append(construct_js_item(item, self.store_current_icon(item)))

        return items


    @api.in_main_thread
    def _show_menu(self, id):
        
        item = self.host.get_item_by_id(id)
        # Show the menu.
        item.show_menu()


    @api.expose
    def show_menu(self, id):

        self._show_menu(id)

