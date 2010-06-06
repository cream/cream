#!/usr/bin/env python

from cream.contrib.melange import api
from cream.util import random_hash

import os
import base64

@api.register('sketch')
class Sketch(api.API):

    def __init__(self):
        api.API.__init__(self)

    @api.expose
    def save_image(self, string64):
        string64 = string64.replace('data:image/png;base64,', '')
        filename = 'sketch' + random_hash(100)[:5] + '.png'
        path = os.path.join(os.path.expanduser('~'), filename)
        with open(path, 'w') as file_:
            s = base64.decodestring(string64)
            file_.write(s)

    
