#!/usr/bin/env python

# note: this is just a workaround until manifests are extended

from os.path import join, dirname

categories = {
    'org.cream.SimplePanel.CategoryAll': {
        'name': 'All',
        'icon': join(dirname(__file__), 'images/melange.png'),
        'description': 'All applets live here. Happily ever after'
    }

}
