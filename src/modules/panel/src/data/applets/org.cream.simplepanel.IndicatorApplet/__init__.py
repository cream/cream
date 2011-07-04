import re
import time
import gobject
import gtk
import cairo

import simplepanel.applet

from indicator import IndicatorObject, IndicatorLoadingFailed


FONT = ('Droid Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
FONT_SIZE = 14
COLOR = (.1, .1, .1, 1)
PADDING = 5
SPACING = 3


INDICATORS = [
    'application',
    'networkmenu',
    'soundmenu',
    'messaging',
    'me',
    'datetime',
    'session'
]


@simplepanel.applet.register
class ApplicationIndicatorApplet(simplepanel.applet.Applet):

    def __init__(self):
        simplepanel.applet.Applet.__init__(self)

        self.connect('click', self.click_cb)

        self.indicators = []

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
                entry.connect('update', lambda *args: self.update())


    def update(self):
        self.allocate(self.get_allocation()[1])
        self.draw()


    def entry_added_cb(self, indicator, entry):

        entry.connect('update', lambda *args: self.update())

        self.allocate(self.get_allocation()[1])
        self.draw()


    def entry_removed_cb(self, indicator, entry):

        entry.connect('update', lambda *args: self.update())

        self.allocate(self.get_allocation()[1])
        self.draw()


    def get_entry_at_coords(self, x, y):

        position = PADDING
        for indicator in self.indicators:
            if position != PADDING:
                position += SPACING
            for entry in indicator.get_entries():
                width = self._get_width_for_entry(entry)
                if x >= position and x <= position + width + PADDING:
                    return entry, position
                position += width
        return None, None


    def click_cb(self, applet, x, y):
        
        entry, position = self.get_entry_at_coords(x, y)

        if self.active_menu:
            if self.active_menu[0] == entry.menu and time.time() - self.active_menu[1] <= .1:
                return

        if entry:
            menu = entry.menu
            
            x, y = position + self.get_position()[0] + SPACING , self.get_allocation()[1]

            menu.popup(None, None, lambda *_: (int(x), int(y), True), 1, 0,)
            def visibility_changed_cb(menu):
                self.active_menu = (menu, time.time())
            menu.connect('deactivate', visibility_changed_cb)

            self.active_menu = (menu, True)


    def render(self, ctx):

        position = PADDING

        for indicator in self.indicators:
            for entry in indicator.get_entries():
                if entry.pixbuf:
                    if position != PADDING:
                        position += SPACING

                    icon_surface, width, height = self._pixbuf_to_surface(entry.pixbuf)
                    ctx.set_source_surface(icon_surface,
                                           position,
                                           (self.get_allocation()[1] - height) / 2)
                    ctx.paint()

                    position += width
                if entry.label:
                    if position != PADDING:
                        position += SPACING

                    ctx.set_operator(cairo.OPERATOR_OVER)
                    ctx.set_source_rgba(*COLOR)
                    ctx.select_font_face(*FONT)
                    ctx.set_font_size(FONT_SIZE)

                    x_bearing, y_bearing, width, height = ctx.text_extents(entry.label)[:4]
                    ctx.move_to(position, (24 - height) / 2 - y_bearing)
                    ctx.show_text(entry.label)
                    ctx.stroke()

                    position += width + x_bearing


    def allocate(self, height):

        width = PADDING

        for indicator in self.indicators:
            if width != PADDING:
                width += SPACING
            width += self._get_width_for_indicator(indicator)

        width += PADDING

        self.set_allocation(width, height)

        return self.get_allocation()


    def _pixbuf_to_surface(self, pixbuf):

        icon_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          pixbuf.get_width(),
                                          pixbuf.get_height())
        icon_context = gtk.gdk.CairoContext(cairo.Context(icon_surface))
        icon_context.set_source_pixbuf(pixbuf, 0, 0)
        icon_context.paint()

        height = icon_surface.get_height()
        width = icon_surface.get_width()

        return icon_surface, width, height


    def _get_width_for_indicator(self, indicator):

        width = 0
        for entry in indicator.get_entries():
            if width != 0:
                width += SPACING
            width += self._get_width_for_entry(entry)

        return width


    def _get_width_for_entry(self, entry):

        width = 0
        if entry.pixbuf:
            if width != 0:
                width += SPACING
            width += entry.pixbuf.get_width()
        if entry.label:
            if width != 0:
                width += SPACING
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
            ctx = cairo.Context(surface)
            ctx.select_font_face(*FONT)
            ctx.set_font_size(FONT_SIZE)
            x_bearing, _, text_width, _ = ctx.text_extents(entry.label)[:4]
            width += text_width + x_bearing

        return width
