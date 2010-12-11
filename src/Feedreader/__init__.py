from melange import api

from feedparser import parse

@api.register('feedreader')
class Feedreader(api.API):

    def __init__(self):
    
        api.API.__init__(self)

    @api.expose
    def get_feeds(self, url):
        data = parse(url)['entries']
        feeds = []
        if data[0].has_key('summary_detail'):
            for feed in data:
                feeds.append({'title': feed['summary_detail']['value'],
                                'link': feed['link'] })
        else:
            feeds = data

        return feeds

