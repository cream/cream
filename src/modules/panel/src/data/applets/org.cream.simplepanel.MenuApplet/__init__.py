import gobject
import gtk
import cairo
import re
import thread

from collections import defaultdict

import simplepanel.applet

from cream.util.subprocess import Subprocess
from cream.xdg.desktopentries import DesktopEntry

from simplepanel.ui import Bubble
from menuitem import MenuItem

PADDING = 5
KICK = re.compile('%[ifFuUck]')

CATEGORIES = {
        "AudioVideo": ('Multimedia', 'applications-multimedia'),
        "Audio": ('Multimedia', 'applications-multimedia'),
        "Video": ('Multimedia', 'applications-multimedia'),
        "Multimedia": ('Multimedia', 'applications-multimedia'),
        "Development": ('Development', 'applications-development'),
        "Education": ('Education', 'applications-science'),
        "Games": ('Games', 'applications-games'),
        "Game": ('Games', 'applications-games'),
        "Graphics": ('Graphics', 'applications-graphics'),
        "Network": ('Network', 'applications-internet'),
        "Office": ('Office', 'applications-office'),
        "Settings": ('Settings', 'applications-engineering'),
        "System": ('System', 'applications-system'),
        "Utility": ('Utility', 'applications-other'),
    }

MENU_CATEGORIES = ['Network', 'Graphics', 'Office', 'Development', 'Multimedia', 'Games', 'Utility', 'System', 'Settings']

class Category(gobject.GObject):

    __gtype_name__ = 'Category'
    __gsignals__ = {
        'hide': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }

    def __init__(self, id_):

        gobject.GObject.__init__(self)

        self.id = id_
        self.single_columned = False

        self.bubble = Bubble()

        self.layout = gtk.VBox()
        self.layout.set_spacing(2)
        self.layout.show_all()

        self.bubble.add(self.layout)

        self.wrapper = gtk.HBox()
        self.layout.pack_start(self.wrapper)
        self.wrapper_children = 0

        self.bubble.window.connect('button-press-event', self.bubble_button_press_cb)


    def show(self, x, y):

        self.bubble.show(x, y)
        while gtk.events_pending():
            gtk.main_iteration()
        gtk.gdk.pointer_grab(self.bubble.window.window, owner_events=True, event_mask=self.bubble.window.get_events() | gtk.gdk.BUTTON_PRESS_MASK)


    def hide(self):

        gtk.gdk.pointer_ungrab()
        self.bubble.hide()
        self.emit('hide')


    def bubble_button_press_cb(self, source, event):

        if event.x <= self.bubble.window.allocation.x\
            or event.y <= self.bubble.window.allocation.y\
            or event.x >= self.bubble.window.allocation.x + self.bubble.window.allocation.width\
            or event.y >= self.bubble.window.allocation.y + self.bubble.window.allocation.height:
                gtk.gdk.pointer_ungrab()
                self.bubble.hide()
                self.emit('hide')


    def add_item(self, desktop_entry):

        if desktop_entry.has_option_default('NoDisplay') and desktop_entry.no_display:
            return


        item = MenuItem(desktop_entry)
        item.connect('button-release-event', self.button_release_cb)
        item.show()

        if self.single_columned:
            self.layout.pack_start(item, False, True)
        else:
            if self.wrapper_children == 2:
                self.wrapper = gtk.HBox()
                self.layout.pack_start(self.wrapper, False, True)
                self.wrapper_children = 0

            self.wrapper.pack_start(item, False, True)
            self.wrapper_children += 1


    def button_release_cb(self, source, event):

        self.bubble.hide()
        self.emit('hide')

        exec_ = KICK.sub('', source.desktop_entry.exec_)

        Subprocess([exec_.strip()]).run()


@simplepanel.applet.register
class MenuApplet(simplepanel.applet.Applet):

    def __init__(self):
        simplepanel.applet.Applet.__init__(self)

        self.default_size = 22
        self.padding = 5

        self.single_column_max_items = self.config.single_column_max_items
        self._active_menu = None

        self.connect('click', self.click_cb)
        self.connect('mouse-motion', self.mouse_motion_cb)

        self.config.connect('field-value-changed', self.config_value_changed_cb)

        self.categories = []

        for cat in MENU_CATEGORIES:
            category = Category(CATEGORIES[cat][0])
            category.connect('hide', self.menu_hide_cb)
            self.categories.append(category)

        thread.start_new_thread(self.fill_categories, ())


    def fill_categories(self):

        self.desktop_entries = defaultdict(list)

        for desktop_entry in DesktopEntry.get_all():
            category = CATEGORIES.get(desktop_entry.recommended_category)
            if category:
                self.desktop_entries[category[0]].append(desktop_entry)

        for category in self.categories:
            entries = self.desktop_entries[category.id]
            entries.sort(key=lambda entry: entry.name.lower())

            category.single_columned = len(entries) <= self.single_column_max_items
            for entry in entries:
                category.add_item(entry)


    def menu_hide_cb(self, source):
        if self._active_menu == source:
            self._active_menu = None


    def get_category_at_coords(self, x, y):

        for c, category in enumerate(self.categories):
            w = h = self.default_size
            x0, y0 = PADDING + c * (w + PADDING), 1
            x1, y1 = x0 + w, y0 + h
            if x >= x0 and x <= x1 and y >= y0 and y <= y1:
                return (category, x0, x1-x0)

        return (None, None, None)


    def click_cb(self, applet, x, y):

        category, position, width = self.get_category_at_coords(x, y)
        if not category:
            return

        if self._active_menu == category:
            self._active_menu.hide()
        elif self._active_menu != category and self._active_menu:
            self._active_menu.hide()
            x = position + width/2 + self.get_position()[0]
            category.show(x, self.get_allocation()[1] + 1)
            self._active_menu = category
        else:
            x = position + width/2 + self.get_position()[0]
            category.show(x, self.get_allocation()[1] + 1)
            self._active_menu = category


    def mouse_motion_cb(self, applet, x, y):

        category, position, width = self.get_category_at_coords(x, y)
        if not category:
            return

        if category != self._active_menu and self._active_menu:
            self._active_menu.hide()
            x = position + width/2 + self.get_position()[0]
            category.show(x, self.get_allocation()[1] + 1)
            self._active_menu = category


    def config_value_changed_cb(self, sender, field, value):

        if self.single_column_max_items == value:
            return

        for category in self.categories:
            entries = self.desktop_entries[category.id]
            single_columned = len(entries) < value
            if category.single_columned != single_columned:
                category.single_columned = single_columned

                for child in category.layout:
                    child.destroy()

                for entry in self.desktop_entries[category.id]:
                    category.add_item(entry)

        self.single_column_max_items = value


    def get_size(self):

        allocation = self.get_allocation()
        if allocation is not None:
            return allocation[1]
        else:
            return self.default_size


    def render(self, ctx):

        position = PADDING

        for category in self.categories:
            icon_name = CATEGORIES[category.id][1]
            theme = gtk.icon_theme_get_default()
            icon_info = theme.lookup_icon(icon_name, 22, 0)
            pb = gtk.gdk.pixbuf_new_from_file(icon_info.get_filename())
            pb = pb.scale_simple(22, 22, gtk.gdk.INTERP_HYPER)

            width = height = 22

            ctx.set_source_pixbuf(pb, position, (self.get_allocation()[1] - height) / 2)
            ctx.paint()

            position += width + self.padding


    def allocate(self, height):

        width = PADDING

        for category in self.categories:
            width += self.get_size() + PADDING

        self.set_allocation(width, height)

        return self.get_allocation()
