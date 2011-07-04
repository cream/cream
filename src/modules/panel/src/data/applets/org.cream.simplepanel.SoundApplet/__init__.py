import gobject
import gtk
import cairo
import re
import thread
import time

import simplepanel.applet
from simplepanel.ui import Bubble

from pulseaudio import PulseAudio

PADDING = 5
STEP = 5

@simplepanel.applet.register
class SoundApplet(simplepanel.applet.Applet):

    def __init__(self):
        simplepanel.applet.Applet.__init__(self)

        self.pulseaudio = PulseAudio('Cream Volume Applet')
        self.pulseaudio.connect()
        while not self.pulseaudio.sinks:
            time.sleep(0.01)

        self.icon_size = 22
        self.menu_active = False
        self.icon = self._get_icon_for_volume(self.pulseaudio.get_volume()[0])

        self.menu = Bubble()

        self.volume_scale = gtk.HScale()
        self.volume_scale.set_range(0, 100)
        self.volume_scale.set_size_request(200, -1)
        self.volume_scale.set_draw_value(False)
        self.volume_scale.set_value(self.pulseaudio.get_volume()[0])

        self.layout = gtk.HBox()
        self.layout.pack_start(self.volume_scale)

        self.menu.add(self.layout)

        self.connect('click', self.toggle_menu_cb)
        self.connect('scroll', self.scroll_cb)
        self.volume_scale.connect('change-value', self.value_changed_cb)


    def change_volume(self, volume):

        volume = int(volume)

        self.pulseaudio.set_volume([volume, volume])
        self.volume_scale.set_value(volume)

        self.icon = self._get_icon_for_volume(volume)
        self.draw()


    def _get_icon_for_volume(self, volume):

        if volume <= 0:
            return 'audio-volume-muted'
        elif volume <= 30:
            return 'audio-volume-low'
        elif volume <= 66:
            return 'audio-volume-medium'
        else:
            return 'audio-volume-high'



    def toggle_menu_cb(self, applet, x, y):

        if self.menu_active:
            self.menu.hide()
        else:
            self.menu.show(int(self.get_position()[0]), self.get_allocation()[1] + 1)

        self.menu_active = not self.menu_active


    def scroll_cb(self, applet, x, y, direction):

        volume = self.pulseaudio.get_volume()[0]
        if direction == gtk.gdk.SCROLL_UP:
            if volume + STEP >= 100:
                volume = 100
            else:
                volume += STEP
        elif direction == gtk.gdk.SCROLL_DOWN:
            if volume - STEP <= 0:
                volume = 0
            else:
                volume -= STEP

        self.change_volume(volume)


    def value_changed_cb(self, scale, scroll_type, volume):

        self.change_volume(volume)


    def render(self, ctx):

        theme = gtk.icon_theme_get_default()
        icon_info = theme.lookup_icon(self.icon, self.icon_size, 0)
        pb = gtk.gdk.pixbuf_new_from_file(icon_info.get_filename())
        pb = pb.scale_simple(self.icon_size, self.icon_size, gtk.gdk.INTERP_HYPER)

        ctx.set_source_pixbuf(pb, PADDING, (self.get_allocation()[1] - self.icon_size) / 2)
        ctx.paint()



    def allocate(self, height):

        self.set_allocation(self.icon_size + PADDING, height)
        return self.get_allocation()
