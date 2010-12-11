#!/usr/bin/env python

from melange import api

import feedparser
import re

import time

PUSH_RE = re.compile(r'^(?P<user>.*) pushed to (?P<branch>.*) at (?P<repo>.*)')

@api.register('github')
class GitHub(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.data = None


    def get_data(self):
        self.data = feedparser.parse(self.config.feed)


    def get_push_notifications(self):

        self.get_data()
        notifications = []

        for entry in self.data.entries:
            m = PUSH_RE.match(entry.title)
            if m:
                notifications.append({
                    'user': m.group('user'),
                    'branch': m.group('branch'),
                    'repo': m.group('repo'),
                    'date': entry.published_parsed
                    })

        return notifications


    @api.expose
    def reset(self):
        self.config.last_update = time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime())


    @api.expose
    def query(self):

        try:
            last_update = time.strptime(self.config.last_update, '%a, %d %b %Y %H:%M:%S +0000')
        except:
            last_update = time.gmtime(0)

        for i in self.get_push_notifications():
            if i['date'] > last_update:
                return True

        return False
    
