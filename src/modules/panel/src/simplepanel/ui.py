#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os
import gtk
import cairo
import cream.gui.svg

MARGIN = 5

class BubbleWindow(gtk.Window):

    def __init__(self):

        gtk.Window.__init__(self)

        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # Setting up the Widget's window...
        self.set_keep_above(True)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_resizable(False)
        self.set_colormap(self.get_screen().get_rgba_colormap())

        self.set_events(self.get_events() | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.POINTER_MOTION_MASK)

        self.display = self.get_display()
        self.screen = self.display.get_default_screen()

        self.connect('expose-event', self.expose_cb)
        self.connect('size-allocate', self.size_allocate_cb)
        self.connect('realize', self.realize_cb)

        self._render_background()


    def set_tip_position(self, tip_x, tip_y):

        x = tip_x - MARGIN - 20 - 10
        if x <= 0:
            left = 20 + x
            self._render_background(max(0, left))
        if x > self.screen.get_width() - self.get_size()[0]:
            left = self.get_size()[0] - (self.screen.get_width() - tip_x)
            self._render_background(left)


        self.move(max(0, x), tip_y - MARGIN)


    def size_allocate_cb(self, source, allocation):
        self._render_background()


    def _render_background(self, left=20):

        window_width, window_height = self.get_size()

        margin = MARGIN

        tip_width = 10
        tip_height = 10

        tip_x = left + tip_width + margin + .5
        tip_y = margin + .5

        width = window_width - 2*margin
        height = window_height - 2*margin - 10

        right = width - (2*tip_width) - left

        path = 'm{tip_x},{tip_y} -{tip_width},{tip_height} -{left},0 0,{height} {width},0 0,-{height} -{right},0 -{tip_width},-{tip_height} z'.format(
            tip_width=tip_width,
            tip_height=tip_height,
            tip_x=tip_x,
            tip_y=tip_y,
            width=width,
            height=height,
            left=left,
            right=right
            )

        # Draw the background…
        self.background_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                     self.get_size()[0],
                                                     self.get_size()[1])
        background_ctx = cairo.Context(self.background_surface)

        background = cream.gui.svg.Handle(os.path.join(self.base_path, 'background.svg'))
        background.dom.getElementById('page').setAttribute('width', str(window_width))
        background.dom.getElementById('page').setAttribute('height', str(window_height))
        background.dom.getElementById('shadow').setAttribute('d', path)
        background.dom.getElementById('border').setAttribute('d', path)
        background.dom.getElementById('background').setAttribute('d', path)
        background.save_dom()
        background.render_cairo(background_ctx)


    def realize_cb(self, window):
        self.window.set_events(self.window.get_events() | gtk.gdk.BUTTON_RELEASE_MASK)
        self.window.property_change("_NET_WM_STRUT", "CARDINAL", 32, gtk.gdk.PROP_MODE_REPLACE, [0, 0, 24, 0])
        #self.window.input_shape_combine_region(gtk.gdk.region_rectangle((0, 0, self.get_size()[0], 24)), 0, 0)


    def expose_cb(self, source, event):
        """ Clear the widgets background. """

        ctx = source.window.cairo_create()

        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.paint()

        ctx.set_operator(cairo.OPERATOR_OVER)

        ctx.set_source_surface(self.background_surface)
        ctx.paint()


class Bubble(object):

    def __init__(self):

        self.window = BubbleWindow()

        self.alignment = gtk.Alignment()
        self.alignment.set_padding(MARGIN + 15 + 5, MARGIN + 5, MARGIN + 5, MARGIN + 5)
        self.window.add(self.alignment)

        self.add = self.alignment.add
        self.remove = self.alignment.remove


    def show(self, tip_x=None, tip_y=None):

        self.window.show_all()

        if tip_x and tip_y:
            self.window.set_tip_position(tip_x, tip_y)


    def hide(self):

        self.window.hide()
