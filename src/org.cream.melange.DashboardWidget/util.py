#!/usr/bin/env python

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import re
import gtk
import base64
import os.path

from cream.util.string import crop_string, slugify
from cream.xdg.desktopentries.gtkmenu import lookup_icon

KICK = re.compile('%[ifFuUck]')
ICON_SIZE = 40

CATEGORIES = {'Development': 'Development',
              'AudioVideo': 'Multimedia',
              'Network': 'Network',
              'Office': 'Office',
              'Settings': 'Settings',
              'System': 'System',
              'Game': 'Games',
              'Graphics': 'Graphics',
              'Utility': 'Utility'
}


def app_from_entry(entry, path):
    if not hasattr(entry, 'icon'):
        return None

    path = os.path.join(path, slugify(entry.name)) + '.png'
    if not save_icon(entry.icon, path):
        return None

    app = {}
    app['name'] = entry.name
    app['label'] = crop_string(entry.name, 8, '..')
    app['cmd'] = KICK.sub('', entry.exec_)
    app['icon'] = os.path.split(path)[1]
    app['category'] = CATEGORIES.get(entry.recommended_category, '')
    return app


def icon_to_base64(icon):
    if '.png' in icon:
        icon = icon.replace('.png', '')
    pixbuf = lookup_icon(icon, ICON_SIZE)
    if pixbuf is None:
        pixbuf = lookup_icon(os.path.split(icon)[1], ICON_SIZE)
        if pixbuf is None:
            return ''
    elif pixbuf.get_width() > ICON_SIZE or pixbuf.get_height() > ICON_SIZE:
        pixbuf = pixbuf.scale_simple(ICON_SIZE, ICON_SIZE, gtk.gdk.INTERP_HYPER)

    data = StringIO()
    def _callback(buf):
        data.write(buf)
    pixbuf.save_to_callback(_callback, 'png')
    icon64 = data.getvalue().encode('base64')
    return icon64

def save_icon(icon, path):
    icon64 = icon_to_base64(icon)
    if not icon:
        return False

    icon64 = icon64.replace('data:image/png;base64,', '')
    if not os.path.exists(path):
        with open(path, 'w') as file_handle:
            s = base64.decodestring(icon64)
            file_handle.write(s)
    return True
