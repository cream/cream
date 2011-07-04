#!/usr/bin/env python

import gtk
from os.path import join, dirname
from collections import defaultdict

from categories import categories

class AddAppletDialog(object):

    def __init__(self, applets):
        self.applets = defaultdict()

        interface = gtk.Builder()
        interface.add_from_file(join(dirname(__file__), 'add_dialog.glade'))

        self.dialog =  interface.get_object('dialog')
        self.category_liststore =  interface.get_object('categories')
        self.category_view =  interface.get_object('category_view')
        self.applet_liststore =  interface.get_object('applets')
        self.applet_view =  interface.get_object('applet_view')
        self.category_image =  interface.get_object('category_image')
        self.category_description =  interface.get_object('category_description')

        # connect signals
        self.dialog.connect('delete_event', lambda *x: self.dialog.hide())
        self.category_view.connect('cursor-changed',
                                    lambda *x: self.on_category_change()
        )

        # add the categories to the liststore alphabetically
        categories_ = sorted(categories.iteritems(),
                             key=lambda c: c[1]['name']
        )
        for id, category in categories_:
            icon = gtk.gdk.pixbuf_new_from_file_at_size(category['icon'], 25, 25)
            self.category_liststore.append((category['name'], id, icon))

        # group applets into categories
        for applet in applets:
            if not applet.get('categories'):
                category = 'org.cream.SimplePanel.CategoryAll'
                self._add_to_category(category, applet)
            for category in applet['categories']:
                self._add_to_category(category['id'], applet)

        self.category_view.set_cursor(0)

    def _add_to_category(self, category, applet):
        if category in self.applets:
            self.applets[category].append(applet)
        else:
            self.applets[category] = [applet]

    def update_info_bar(self):
        """
        Update the description of a category which is displayed above
        the applet listview
        """

        category = categories[self.selected_category]
        if 'icon' in category:
            icon = gtk.gdk.pixbuf_new_from_file_at_size(category['icon'], 35, 35)
            self.category_image.set_from_pixbuf(icon)

        description = split_string(category['description'])
        self.category_description.set_text(description)

    def on_category_change(self):
        """
        Whenever a new category is selected, clear the liststore and add the
        applets corresponding to the category to it
        """

        self.applet_liststore.clear()
        self.update_info_bar()
        category = self.selected_category
        if not category in self.applets:
            return

        for applet in self.applets[category]:
            if 'icon' in applet:
                path = applet['icon']
            else:
                path = join(dirname(__file__), 'images/melange.png')

            icon = gtk.gdk.pixbuf_new_from_file_at_size(path, 35, 35)
            label = '<b>{0}</b>\n{1}'.format(applet['name'],
                                             split_string(applet['description'])
                                      )
            self.applet_liststore.append((icon, label, applet['name'], applet['id']))

    @property
    def selected_applet(self):
        selection = self.applet_view.get_selection()
        model, iter = selection.get_selected()
        return model.get_value(iter, 3)

    @property
    def selected_category(self):
        selection = self.category_view.get_selection()
        model, iter = selection.get_selected()
        return model.get_value(iter, 1)

def split_string(description):
    """split a long string into multiple lines"""
    lst = []
    chars = 0
    for word in description.split():
        if chars > 30:
            lst.append('\n')
            chars = 0
        lst.append(word)
        chars += len(word)

    return ' '.join(lst)
