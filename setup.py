#!/usr/bin/env python

import os
from distutils.core import setup

def collect_data_files():

    data_files = []

    for directory, directories, files in os.walk('src'):
        rel_dir = directory.replace('src/', '')
        for file_ in files:
            data_files.append((
                    os.path.join('share/cream/org.cream.Melange/data/widgets', rel_dir),
                    [os.path.join(directory, file_)]
            ))

    return data_files


data_files = collect_data_files()

setup(
    name = 'melange-widgets',
    version = '0.4.8',
    author = 'The Cream Project (http://cream-project.org)',
    url = 'http://github.com/cream/melange-widgets',
    data_files = data_files,
)
