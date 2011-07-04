import cairo
import rsvg

import ooxcb
from ooxcb.protocol import xproto

import simplepanel.applet

TIMEOUT = 5

@simplepanel.applet.register
class ScreensaverApplet(simplepanel.applet.Applet):

    def __init__(self):

        simplepanel.applet.Applet.__init__(self)

        self.connection = ooxcb.connect()

        self.screensaver_timeout = 0
        self.toggle_screensaver

        self.icon_active = rsvg.Handle('data/applets/org.cream.simplepanel.ScreensaverApplet/screensaver_active.svg')
        self.icon_inactive = rsvg.Handle('data/applets/org.cream.simplepanel.ScreensaverApplet/screensaver_inactive.svg')

        self.connect('click', lambda *args: self.toggle_screensaver())

        self.draw()


    def toggle_screensaver(self):

        if self.screensaver_timeout == TIMEOUT:
            self.screensaver_timeout = 0
        else:
            self.screensaver_timeout = TIMEOUT

        self.connection.core.set_screen_saver(self.screensaver_timeout, 0, 0, 0)
        self.connection.flush()

        self.draw()


    def render(self, ctx):

        ctx.set_operator(cairo.OPERATOR_OVER)

        if self.screensaver_timeout == TIMEOUT:
            icon = self.icon_active
        else:
            icon = self.icon_inactive

        height = float(self.get_allocation()[1] - 8)
        icon_height = float(icon.get_dimension_data()[1])

        ctx.translate(2, 4)
        ctx.scale(height/icon_height, height/icon_height)
        icon.render_cairo(ctx)

        ctx.stroke()


    def allocate(self, height):

        icon_width = self.icon_active.get_dimension_data()[0]
        icon_height = self.icon_active.get_dimension_data()[1]

        self.set_allocation(icon_width * (float(height - 8) / float(icon_height)) + 4, height)
        return self.get_allocation()
