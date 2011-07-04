import gtk
import gobject

import ooxcb
import ooxcb.contrib.ewmh, ooxcb.contrib.icccm
from ooxcb.protocol import xproto
from ooxcb.contrib.ewmh import ewmh_get_desktop as get_desktop
from ooxcb.contrib.ewmh import ewmh_get_current_desktop as get_current_desktop

ooxcb.contrib.ewmh.mixin()
ooxcb.contrib.icccm.mixin()

from cream.util import cached_property
from cream.util.pywmctrl import Screen
from util import convert_icon

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


class Windows(gobject.GObject):
    __gsignals__ = {
        'windows-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_PYOBJECT, ())
        }

    def __init__(self, icon_size):
        gobject.GObject.__init__(self)

        self.icon_size = icon_size

        self.conn = ooxcb.connect()
        self.screen = self.conn.setup.roots[self.conn.pref_screen]
        self.root = self.screen.root
        self.pywmctrl = Screen(self.conn, self.root)

        self.ignore_window_types = map(
                lambda name: self.conn.atoms['_NET_WM_WINDOW_TYPE_%s' % name].get_internal(),
                IGNORE_WINDOW_TYPES)

        self.windows_by_desktop = self.collect_windows()

        with self.conn.bunch():
            self.root.change_attributes(event_mask=xproto.EventMask.PropertyChange)
        self.root.push_handlers(on_property_notify=self.on_property_notify)

        self._setup_mainloop()


    def collect_windows(self):
        windows_by_desktop = {}
        for window in self.screen.ewmh_get_client_list():
            if not self.ignore_window(window):
                desktop = get_desktop(window)

                if desktop in windows_by_desktop:
                    windows_by_desktop[desktop].append(Window(window, self.icon_size))
                else:
                    windows_by_desktop[desktop] = [Window(window, self.icon_size)]
        return windows_by_desktop


    def on_property_notify(self, event):
        if event.atom == self.conn.atoms['_NET_CLIENT_LIST'] \
            and event.state == xproto.Property.NewValue:
                self.windows_by_desktop = self.collect_windows()
                self.emit('windows-changed')


    def ignore_window(self, window):
        state = window.get_property('_NET_WM_STATE', 'ATOM').reply().value
        if self.conn.atoms['_NET_WM_STATE_SKIP_TASKBAR'].get_internal() in state:
            return True
        type = window.get_property('_NET_WM_WINDOW_TYPE', 'ATOM').reply().value
        if any(t for t in type if t in self.ignore_window_types):
            return True
        return False

    def toggle_window(self, window):
        with self.conn.bunch():
            self.pywmctrl._send_clientmessage(
                window._window,
                '_NET_ACTIVE_WINDOW',
                32,
                [1, window._window.get_internal(), 0]
            )
            self.conn.flush()
        #self.pywmctrl._send_clientmessage(
            #window._window,
            #'_NET_WM_STATE',
            #32,
            #[2, 0, 0, 1]
        #)

    def _ooxcb_cb(self, source, cb_condition):
        while self.conn.alive:
            event = self.conn.poll_for_event()
            if event is not None:
                event.dispatch()
            return True

    def _setup_mainloop(self):
        gobject.io_add_watch(
                    self.conn.get_file_descriptor(),
                    gobject.IO_IN,
                    self._ooxcb_cb
        )

    @property
    def all(self):
        return self.windows_by_desktop


    @property
    def on_current_desktop(self):
        current_desktop = get_current_desktop(self.screen)
        return self.windows_by_desktop[current_desktop]


class Window(object):

    def __init__(self, window, icon_size):
        self._window = window
        self.icon_size = icon_size

        theme = gtk.icon_theme_get_default()
        self.icon_fallback = theme.lookup_icon('gnome-unknown', self.icon_size, 0).get_filename()


    def to_dict(self):
        return {
            'icon': self.icon,
            'xid': self._window.xid,
            'state': self.state,
            'title': self.title
        }

    @cached_property
    def icon(self):
        icon_data = self._window.get_property('_NET_WM_ICON', 'CARDINAL').reply()
        if icon_data.value:
            icon = convert_icon(icon_data.value, self.icon_size)
        else:
            icon = gtk.gdk.pixbuf_new_from_file_at_size(self.icon_fallback, self.icon_size, self.icon_size)
        return icon


    @cached_property
    def title(self):
        return self._window.ewmh_get_window_name()


    @cached_property
    def state(self):
        return self._window.icccm_get_wm_state()

if __name__ == '__main__':
    windows = Windows()
