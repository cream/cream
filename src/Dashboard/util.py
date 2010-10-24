#!/usr/bin/env python

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from cream.contrib.desktopentries.gtkmenu import lookup_icon

ICON_SIZE = 40

def icon_to_base64(icon):
    pixbuf = lookup_icon(icon, ICON_SIZE)
    if pixbuf is None:
        return ''

    data = StringIO()
    def _callback(buf):
        data.write(buf)
    pixbuf.save_to_callback(_callback, 'png')
    base64 = data.getvalue().encode('base64')
    return base64
