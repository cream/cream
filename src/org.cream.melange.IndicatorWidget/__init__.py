#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import hashlib
import gtk

from melange import api

from indicator import IndicatorObject, IndicatorLoadingFailed

def construct_js_item(item, icon_filename):
    return {
        'icon': icon_filename,
        'id': item.id,
    }

INDICATORS = [
    'application',
    'networkmenu',
    'soundmenu',
    'messaging',
    'me',
    'datetime',
    'session'
]

@api.register('indicators')
class AppIndicators(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.indicators = []
        self.entries = {}

        self.active_menu = None

        self.screen_width = gtk.gdk.screen_width()

        for indicator_name in INDICATORS:
            path = '/usr/lib/indicators/4/lib{name}.so'.format(name=indicator_name)

            try:
                indicator = IndicatorObject(path)

                indicator.connect('entry-added', self.entry_added_cb)
                indicator.connect('entry-removed', self.entry_removed_cb)

                self.indicators.append(indicator)
            except IndicatorLoadingFailed:
                pass

        for indicator in self.indicators:
            for entry in indicator.get_entries():
                entry.connect('update', self.entry_update_cb)
                self.entries[hashlib.md5(str(entry)).hexdigest()] = entry
                html_entry = self.convert_entry(entry)
                self.emit('entry-added', html_entry)
                
                
    @api.expose
    def get_entries(self):
    
        entries = []
        
        for indicator in self.indicators:
            for entry in indicator.get_entries():
                entries.append(self.convert_entry(entry))

        return entries
        
        
    def entry_update_cb(self, entry):

        html_entry = self.convert_entry(entry)
        self.emit('entry-updated', html_entry)
        

    def convert_entry(self, entry):
    
        data_path = self.get_data_path()
        entry_id = hashlib.md5(str(entry)).hexdigest()
        icon_name = entry_id + '-' + hashlib.md5(str(time.time())).hexdigest() + '.png'
        icon_path = os.path.join(data_path, icon_name)

        entry.pixbuf.save(icon_path, 'png')
        
        return {
            'id': entry_id,
            'icon': '/data/' + icon_name
        }


    def entry_added_cb(self, indicator, entry):
        html_entry = self.convert_entry(entry)
        self.entries[hashlib.md5(str(entry)).hexdigest()] = entry
        self.emit('entry-added', html_entry)


    def entry_removed_cb(self, indicator, entry):
        del self.entries[hashlib.md5(str(entry)).hexdigest()]
        html_entry = self.convert_entry(entry)
        self.emit('entry-removed', html_entry)


    @api.in_main_thread
    def _show_menu(self, _id):
    
        menu = self.entries[_id].menu
        menu.popup(None, None, None, 1, 0)


    @api.expose
    def show_menu(self, _id):
        self._show_menu(_id)
