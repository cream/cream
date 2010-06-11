#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
import gobject
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import ooxcb
import ooxcb.contrib.ewmh
from ooxcb.protocol import xproto
ooxcb.contrib.ewmh.mixin()

from cream.contrib.melange import api

MIN_DIM = 16

class IconError(Exception):
    pass

def convert_icon(data, desired_size=None):
    length = len(data)
    if length < (MIN_DIM * MIN_DIM + 2):
        raise IconError('Icon too small: Expected %d, got %d' % (MIN_DIM * MIN_DIM + 2, length))
    width = data[0]
    height = data[1]
    # TODO: check size
    rgba_data = ''
    for argb in data[2:]:
        rgba = ((argb << 8) & 0xffffff00) | (argb >> 24)
        rgba_data += chr(rgba >> 24)
        rgba_data += chr((rgba >> 16) & 0xff)
        rgba_data += chr((rgba >> 8) & 0xff)
        rgba_data += chr(rgba & 0xff)
    pb = gtk.gdk.pixbuf_new_from_data(rgba_data, gtk.gdk.COLORSPACE_RGB, True, 8, width, height, width * 4)
    if (desired_size is not None and (width != desired_size or height != desired_size)):
        pb = pb.scale_simple(desired_size, desired_size, gtk.gdk.INTERP_HYPER)
    return pb

@api.register('taskbar')
class Taskbar(api.API):

    def __init__(self):
        api.API.__init__(self)
        self.conn = ooxcb.connect()
        self.screen = self.conn.setup.roots[self.conn.pref_screen]
        self.root = self.screen.root
        self._setup_mainloop()

        with self.conn.bunch():
            self.root.change_attributes(event_mask=xproto.EventMask.PropertyChange)
        self.root.push_handlers(
            on_property_notify=self.on_property_notify,
        )

        self.windows = []

    def on_property_notify(self, evt):
        if evt.atom == self.conn.atoms['_NET_CLIENT_LIST']:
            # new client!
            new_windows = set(self.collect_windows()) - set(self.windows)
            print 'New windows: %r' % new_windows
            for window in filter(self.should_manage_window, new_windows):
                print 'should call self.manage(%r)' % window
                self.manage(window)

    def should_manage_window(self, window):
        state = window.get_property('_NET_WM_STATE', 'ATOM').reply().value
        print 'Should manage %r %r?' % (window, window.ewmh_get_window_name())
        if (self.conn.atoms['_NET_WM_STATE_SKIP_TASKBAR'].get_internal() in state
            or self.conn.atoms['_NET_WM_STATE_HIDDEN'].get_internal() in state):
            print 'Skip Taskbar / Hidden'
            return False
        print 'YES'
        return True

    def collect_windows(self):
        return filter(self.should_manage_window, self.screen.ewmh_get_client_list())

    @api.expose
    def manage_data(self, data):
        self.manage_in_main_thread(self.conn.get_from_cache_fallback(data['xid'], xproto.Window))

    @api.in_main_thread
    def manage_in_main_thread(self, window):
        self.manage(window)

    def manage(self, window):
        #self.emit('item-added', 'yo')
        print '--- managing %r %r' % (window, window.ewmh_get_window_name())
        self.windows.append(window)
        self.emit('window-added', self.to_js(window))

    def get_icon(self, window):
        icon = window.get_property('_NET_WM_ICON', 'CARDINAL').reply()
        if icon.exists:
            print 'has icon.'
            pb = convert_icon(icon.value, 16)
            data = StringIO()
            def _callback(buf):
                data.write(buf)
            pb.save_to_callback(_callback, 'png')
            base64 = data.getvalue().encode('base64')
            return base64
        return ''

    def to_js(self, window):
        return {
            'icon': self.get_icon(window),
            'xid': window.xid
        }

    def ooxcb_callback(self, source, cb_condition):
        while self.conn.alive:
            evt = self.conn.poll_for_event()
            if evt is None:
                break
            evt.dispatch()
        # return True so that the callback will be called again.
        return True

    def _setup_mainloop(self):
        gobject.io_add_watch(
                self.conn.get_file_descriptor(),
                gobject.IO_IN,
                self.ooxcb_callback
        )

#    @api.in_main_thread
#    def _show_menu(self):
#        self.menu.popup(None, None, None, 1, 0)
#
    @api.expose
    def get_all_windows(self):
        return map(self.to_js, self.collect_windows())

