from melange import api

from feedparser import parse


@api.register('org.cream.melange.FeedreaderWidget')
class Feedreader(api.API):

    def __init__(self):

        api.API.__init__(self)

    @api.expose
    def get_feeds(self):
        data = parse(self.config.url)['entries']
        feeds = []
        if 'summary_detail' in data[0]:
            for feed in data:
                feeds.append({
                    'title': feed['summary_detail']['value'],
                    'link': feed['link']
                })
        else:
            for feed in data:
                feeds.append({'title': feed['title'], 'link': feed['link']})

        return feeds[:self.config.number]

