import gobject
import gtk
import cairo
import time


import simplepanel.applet

from windows import Windows

PADDING = 5
ICON_SIZE = 22


@simplepanel.applet.register
class WindowListApplet(simplepanel.applet.Applet):

    def __init__(self):
        simplepanel.applet.Applet.__init__(self)

        self.windows = Windows(ICON_SIZE)
        self.windows.connect('windows_changed', lambda *x: self.draw())

        self.connect('click', self.click_cb)

        self.draw()


    def click_cb(self, source, x, y):
        window = self._get_window_at_coord(x)
        self.windows.toggle_window(window)


    def _get_window_at_coord(self, x):
        position = 0

        for window in self.windows.on_current_desktop:
            if window.icon is not None:
                position += window.icon.get_width() + PADDING
                if x < position:
                    return window


    def render(self, ctx):

        position = PADDING
        for window in self.windows.on_current_desktop:
            icon = window.icon
            if icon is not None:
                height = icon.get_height()
                ctx.set_source_pixbuf(icon, position, (self.allocation[1] - height)/2)
                ctx.paint()

                position += icon.get_width() + PADDING



    def allocate(self, height):
        width = PADDING

        for window in self.windows.on_current_desktop:
            print window.title
            icon = window.icon
            if icon is not None:
                width += icon.get_width() + PADDING

        self.set_allocation(width, height)

        return self.get_allocation()
