import gobject
from gi.repository import Gtk as gtk
import cairo

import cream.ipc

import simplepanel.applet

SIZE = 20
PADDING = 2


@simplepanel.applet.register
class MelangeApplet(simplepanel.applet.Applet):

    def __init__(self):
        simplepanel.applet.Applet.__init__(self)

        self.melange = cream.ipc.get_object('org.cream.Melange', '/org/cream/Melange')
        self.connect('click', self.click_cb)
        self.draw()

    def click_cb(self, applet, x, y):
        self.melange.toggle_overlay()


    def render(self, ctx):

        #icon = gtk.gdk.pixbuf_new_from_file_at_size('melange.png', SIZE, SIZE)
        #icon_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, SIZE, SIZE)
        #icon_context = gtk.gdk.CairoContext(cairo.Context(icon_surface))
        #icon_context.set_source_pixbuf(icon, 0, 0)
        #icon_context.paint()

        #height = icon_surface.get_height()

        #ctx.set_source_surface(icon_surface, PADDING, (self.get_allocation()[1] - height) / 2)
        #ctx.paint()
        pass


    def allocate(self, height):

        self.set_allocation(SIZE + PADDING, height)
        return self.get_allocation()
