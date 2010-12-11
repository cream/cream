#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
import gobject
from threading import Lock
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import ooxcb
import ooxcb.contrib.ewmh, ooxcb.contrib.icccm
from ooxcb.protocol import xproto
ooxcb.contrib.ewmh.mixin()
ooxcb.contrib.icccm.mixin()

from cream.util import cached_property
from cream.util.pywmctrl import Screen
from melange import api

MIN_DIM = 16
DEFAULT_SIZE = 32
MAX_TITLE_LEN = 16

class IconError(Exception):
    pass

xproto.Window.__hash__ = lambda self: hash(self.xid)

IGNORE_WINDOW_TYPES = [
    'DESKTOP',
    'DOCK',
    'TOOLBAR',
    'MENU',
    'SPLASH',
    'UTILITY',
    'DROPDOWN_MENU',
    'POPUP_MENU',
    'TOOLTIP',
    'NOTIFICATION',
    'COMBO',
    'DND',
]

def convert_icon(data, desired_size=DEFAULT_SIZE):
    length = len(data)
    if length < (MIN_DIM * MIN_DIM + 2):
        raise IconError('Icon too small: Expected %d, got %d' % (MIN_DIM * MIN_DIM + 2, length))
    sizes = {}
    start = 0
    while start < length:
        width = data[start]
        height = data[start + 1]
        if width != height:
            start += 2 + width * height
            continue
        rgba_data = ''
        for argb in data[start + 2:start + 2 + width*height]:
            rgba = ((argb << 8) & 0xffffff00) | (argb >> 24)
            rgba_data += chr(rgba >> 24)
            rgba_data += chr((rgba >> 16) & 0xff)
            rgba_data += chr((rgba >> 8) & 0xff)
            rgba_data += chr(rgba & 0xff)
        start += 2 + width * height
        sizes[width] = gtk.gdk.pixbuf_new_from_data(rgba_data, gtk.gdk.COLORSPACE_RGB, True, 8, width, height, width * 4)
    use_pb = None
    biggest = None
    for size, pb in sizes.iteritems():
        if (biggest is None or biggest.get_width() < pb.get_width()):
            biggest = pb
        if size >= desired_size:
            use_pb = pb
    if not sizes:
        return None
    if (use_pb is None or use_pb.get_width() != desired_size):
        use_pb = biggest.scale_simple(desired_size, desired_size, gtk.gdk.INTERP_HYPER)
    return use_pb

@api.register('taskbar')
class Taskbar(api.API):

    def __init__(self):
        api.API.__init__(self)
        self.conn = ooxcb.connect()
        self.screen = self.conn.setup.roots[self.conn.pref_screen]
        self.root = self.screen.root
        self.pywmctrl = Screen(self.conn, self.root)
        self.ignore_window_types = map(
                lambda name: self.conn.atoms['_NET_WM_WINDOW_TYPE_%s' % name].get_internal(),
                IGNORE_WINDOW_TYPES)
        self._setup_mainloop()

        with self.conn.bunch():
            self.root.change_attributes(event_mask=xproto.EventMask.PropertyChange)
        self.root.push_handlers(
            on_property_notify=self.on_property_notify,
        )

        self.windows = []

    def on_client_property_notify(self, evt):
        if evt.window in self.windows:
            # A real client!
            if evt.atom == self.conn.atoms['WM_STATE']:
                self.change_state(evt.window)

    def on_property_notify(self, evt):
        if (evt.atom == self.conn.atoms['_NET_CLIENT_LIST'] and evt.state == xproto.Property.NewValue):
            clients = set(self.collect_windows())
            current = set(self.windows)
            new_windows = clients - current
            removed_windows = current - clients
            for window in new_windows:
                if self.should_manage_window(window):
                    self.manage(window)
            for window in removed_windows:
                self.unmanage(window)

    def should_manage_window(self, window):
        state = window.get_property('_NET_WM_STATE', 'ATOM').reply().value
        if self.conn.atoms['_NET_WM_STATE_SKIP_TASKBAR'].get_internal() in state:
            return False
        type = window.get_property('_NET_WM_WINDOW_TYPE', 'ATOM').reply().value
        if any(t for t in type if t in self.ignore_window_types):
            return False
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
        print '-- Managing: %r, windows: %r' % (window, self.windows)
        self.windows.append(window)
        with self.conn.bunch():
            window.change_attributes(event_mask=xproto.EventMask.PropertyChange)
            window.push_handlers(
                on_property_notify=self.on_client_property_notify
            )
        self.emit('window-added', self.to_js(window, True))

    def unmanage(self, window):
        print '-- Unmanaging: %r, windows: %r' % (window, self.windows)
        self.windows.remove(window)
        self.emit('window-removed', self.to_js(window, add_state=False)) # would result in a BadWindow if state was added.

    @property
    def icon_size(self):
        return self._js_ctx.widget.config.get('icon_size', DEFAULT_SIZE)

    @api.expose
    def get_icon(self, window):
        window = self.conn.get_from_cache_fallback(int(window), xproto.Window)
        return self._get_icon_in_main_thread(window)

    @api.in_main_thread
    def _get_icon_in_main_thread(self, window):
        return self._get_icon(window)

    def _get_icon(self, window):
        icon = window.get_property('_NET_WM_ICON', 'CARDINAL').reply()
        if icon.exists:
            pb = convert_icon(icon.value, self.icon_size)
            if pb is not None:
                data = StringIO()
                def _callback(buf):
                    data.write(buf)
                pb.save_to_callback(_callback, 'png')
                base64 = data.getvalue().encode('base64')
                return base64
        return ''

    def to_js(self, window, add_icon=False, add_state=True):
        icon = self._get_icon(window) if add_icon else None
        return {
            'icon': icon,
            'xid': window.xid,
            'state': self.get_state(window) if add_state else None,
            'title': self.get_short_title(window) if add_state else None,
            'size': self.icon_size,
        }

    def get_short_title(self, window):
        title = ''
        icon_name = window.get_property('WM_ICON_NAME', 'STRING').reply()
        if icon_name.exists:
            title = icon_name.value.to_string()
        else:
            title = window.ewmh_get_window_name()
        if len(title) > MAX_TITLE_LEN:
            title = title[:MAX_TITLE_LEN - 4] + ' ...'
        return title

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

    @api.expose
    def toggle(self, xid):
        window = self.conn.get_from_cache_fallback(xid, xproto.Window)
        self.toggle_in_main_thread(window)

    @api.in_main_thread
    def toggle_in_main_thread(self, window):
        state = window.icccm_get_wm_state()
        if state.state == xproto.WMState.Iconic:
            window.map()
            self.conn.flush()
            result = True
        else:
            self.pywmctrl._send_clientmessage(
                window,
                'WM_CHANGE_STATE',
                32,
                [xproto.WMState.Iconic])
            result = False

    def change_state(self, window):
        self.emit('window-state-changed', self.to_js(window))

    def get_state(self, window):
        state = window.icccm_get_wm_state()
        return (state is not None and state.state == xproto.WMState.Normal)
