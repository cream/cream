#!/usr/bin/env python

from cream.contrib.melange import api
from cream.util import random_hash

import os
import gtk
import base64

@api.register('sketch')
class Sketch(api.API):

    def __init__(self):
        api.API.__init__(self)

        interface = gtk.Builder()
        interface.add_from_file(os.path.join(self.context.working_directory, 'save.glade'))
       
        self.dialog = interface.get_object('dialog')
        self.dialog.connect('delete_event', lambda *args: self.dialog.hide())

        filter = gtk.FileFilter()
        filter.set_name('.png')
        filter.add_mime_type('image/png')
        filter.add_pattern('*.png')
        self.dialog.add_filter(filter)

    def save_image(self, path, string64):
        string64 = string64.replace('data:image/png;base64,', '')
        with open(path, 'w') as file_:
            s = base64.decodestring(string64)
            file_.write(s)

    @api.expose
    def show_save_dialog(self, string64):
        self.dialog.set_current_folder(os.path.expanduser('~'))
        self.dialog.show_all()

        if self.dialog.run() == 1:
            path = self.dialog.get_filename()
            if not path.endswith('.png'):
                path += '.png'
            self.save_image(path, string64)

        self.dialog.hide()

