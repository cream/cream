import gobject
import gtk
import cairo
import time

import simplepanel.applet

FONT = ('Droid Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
FONT_SIZE = 14
COLOR = (.1, .1, .1, 1)
PADDING = 5

@simplepanel.applet.register
class ClockApplet(simplepanel.applet.Applet):

    def __init__(self):
        simplepanel.applet.Applet.__init__(self)

        self.draw()

        gobject.timeout_add(1000, self.update)
        
        self.config.connect('field-value-changed', self.config_changed)
        
        
    def config_changed(self, config, key, value):
        
        try:
            setattr(self.config, key, value)
        except:
            pass
        
        self.reallocate()
        self.update()

        
    def update(self):

        self.draw()
        return True


    def render(self, ctx):

        s = time.strftime(self.config.format)

        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_rgba(*COLOR)
        ctx.select_font_face(*FONT)
        ctx.set_font_size(FONT_SIZE)

        x_bearing, y_bearing, width, height = ctx.text_extents(s)[:4]
        ctx.move_to(PADDING, (24 - height) / 2 - y_bearing)
        ctx.show_text(s)
        ctx.stroke()


    def allocate(self, height):

        s = time.strftime(self.config.format)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, height)
        ctx = cairo.Context(surface)
        ctx.select_font_face(*FONT)

        ctx.set_font_size(FONT_SIZE)

        text_x_bearing, text_y_bearing, text_width, text_height = ctx.text_extents(s)[:4]

        self.set_allocation(text_width + text_x_bearing + 2*PADDING, height)
        return self.get_allocation()
