import os.path
import math
import gtk
import cairo

import cream.gui

def rounded_rectangle(cr, x, y, w, h, r=20):

    if r >= h / 2.0:
        r = h / 2.0

    cr.arc(x + r, y + r, r, math.pi, -.5 * math.pi)
    cr.arc(x + w - r, y + r, r, -.5 * math.pi, 0 * math.pi)
    cr.arc(x + w - r, y + h - r, r, 0 * math.pi, .5 * math.pi)
    cr.arc(x + r, y + h - r, r, .5 * math.pi, math.pi)
    cr.close_path()

def lookup_icon(icon_name):
    theme = gtk.icon_theme_get_default()

    icon_info = theme.lookup_icon(icon_name, 32, 0)
    if icon_info:
        return icon_info.get_filename()
    elif os.path.isfile(icon_name):
        return icon_name
    elif '.' in icon_name:
        icon_name = os.path.splitext(icon_name)[0]
        icon_info = theme.lookup_icon(icon_name, 32, 0)
        if icon_info:
            return icon_info.get_filename()

    icon_info = theme.lookup_icon('application-default-icon', 32, 0)
    return icon_info.get_filename()


class MenuItem(gtk.Widget):

    __gtype_name__ = 'MenuItem'

    def __init__(self, desktop_entry):

        gtk.Widget.__init__(self)

        self.connect('enter-notify-event', self.enter_notify_cb)
        self.connect('leave-notify-event', self.leave_notify_cb)

        self.desktop_entry = desktop_entry

        icon_path = lookup_icon(self.desktop_entry.icon)
        pb = gtk.gdk.pixbuf_new_from_file(icon_path)
        self._icon_pixbuf = pb.scale_simple(32, 32, gtk.gdk.INTERP_HYPER)

        self._entered = False
        self._animation = None
        self._background_alpha = 0


    def enter_notify_cb(self, source, event):

        def update(t, state):
            self._background_alpha = state
            self.draw()

        def completed_cb(source):
            self._animation = None

        if self._animation:
            self._animation.stop()

        t = cream.gui.Timeline(300, cream.gui.CURVE_SINE)
        t.connect('update', update)
        t.connect('completed', completed_cb)
        t.run()
        self._animation = t


    def leave_notify_cb(self, source, event):

        def update(t, state, start):
            self._background_alpha = start - state * start
            self.draw()

        def completed_cb(source):
            self._animation = None

        if self._animation:
            self._animation.stop()

        t = cream.gui.Timeline(300, cream.gui.CURVE_SINE)
        t.connect('update', update, self._background_alpha)
        t.connect('completed', completed_cb)
        t.run()
        self._animation = t


    def event_cb(self, source, event):

        # TODO: Emit leave event when leaving top level widget.
        if event.type == gtk.gdk.LEAVE_NOTIFY and self._entered:
            self._entered = False
            event = gtk.gdk.Event(gtk.gdk.LEAVE_NOTIFY)
            self.emit('leave-notify-event', event)
            while gtk.events_pending():
                gtk.main_iteration()

        try:
            if event.x >= self.allocation.x\
                and event.y >= self.allocation.y\
                and event.x <= self.allocation.x + self.allocation.width\
                and event.y <= self.allocation.y + self.allocation.height:
                    self.event(event)
                    if event.type == gtk.gdk.MOTION_NOTIFY:
                        if not self._entered:
                            self._entered = True
                            event = gtk.gdk.Event(gtk.gdk.ENTER_NOTIFY)
                            self.emit('enter-notify-event', event)
                            while gtk.events_pending():
                                gtk.main_iteration()
            else:
                if event.type == gtk.gdk.MOTION_NOTIFY:
                    if self._entered:
                        self._entered = False
                        event = gtk.gdk.Event(gtk.gdk.LEAVE_NOTIFY)
                        self.emit('leave-notify-event', event)
                        while gtk.events_pending():
                            gtk.main_iteration()
        except:
            pass


    def do_realize(self):

        self.set_flags(self.flags() | gtk.REALIZED | gtk.NO_WINDOW | gtk.SENSITIVE | gtk.PARENT_SENSITIVE)
        self.window = self.get_parent_window()
        self.style.attach(self.window)

        parent = self.get_parent()
        while parent.flags() & gtk.NO_WINDOW:
            parent = parent.get_parent()

        parent.connect('event', self.event_cb)


    def do_size_request(self, requisition):

        width, height = 250, 36
        requisition.width = width
        requisition.height = height


    def do_size_allocate(self, allocation):
        self.allocation = allocation


    def do_expose_event(self, event):
        self._draw()


    def draw(self):

        if self.window:
            self.window.invalidate_rect(self.allocation, True)


    def _draw(self):

        width = self.allocation.width
        height = self.allocation.height

        factor = min(width, height)

        ctx = self.window.cairo_create()
        ctx.set_operator(cairo.OPERATOR_OVER)

        ctx.translate(self.allocation.x, self.allocation.y)
        ctx.set_line_width(1)

        ctx.set_source_rgba(1, 1, 1, .2 * self._background_alpha)
        rounded_rectangle(ctx, 0, 0, 250, 36, 3)
        ctx.fill()

        ctx.set_source_rgba(1, 1, 1, .1 * self._background_alpha)
        rounded_rectangle(ctx, .5, .5, 249, 35, 3)
        ctx.stroke()

        ctx.translate(2, 2)
        ctx.set_source_pixbuf(self._icon_pixbuf, 0, 0)
        ctx.paint()

        pattern = cairo.LinearGradient(0, 0, 248, 35)
        pattern.add_color_stop_rgba(0, .1, .1, .1, 1)
        pattern.add_color_stop_rgba(.9, .1, .1, .1, 1)
        pattern.add_color_stop_rgba(1, .1, .1, .1, 0)
        ctx.set_source(pattern)

        ctx.select_font_face('Droid Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)

        x_bearing, y_bearing, width, height = ctx.text_extents(self.desktop_entry.name)[:4]
        ctx.move_to(36, (32 - height) / 2 - y_bearing)
        ctx.show_text(self.desktop_entry.name)
        ctx.stroke()
