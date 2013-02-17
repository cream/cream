from melange import api

from lxml.etree import parse
from urllib import urlopen
from contextlib import closing

import re

@api.register('org.cream.melange.IdenticaWidget')
class Identica(api.API):

    def __init__(self):

        api.API.__init__(self)

        self.group_template = 'http://identi.ca/api/statusnet/groups/timeline/{0}.xml'
        self.user_template = 'http://identi.ca/api/statuses/user_timeline/{0}.xml'
        self.regex = 'http?://[^ \)]*'

    @api.expose
    def get_data(self):
        name = self.config.name
        if self.config.type == 'group':
            url = self.group_template.format(name)
        else:
            url = self.user_template.format(name)

        with closing(urlopen(url)) as xml:
            raw_data = parse(xml)

        data = []
        posts = raw_data.findall('status')

        for post in posts:
            text = post.find('text').text
            # convert links to <a href>
            try:
                link = re.search(self.regex, text).group().strip()
                text = text.replace(link, '<a href="{0}">{0}</a>'.format(link))
            except:
                pass

            author = post.find('user').find('screen_name').text
            time = post.find('created_at').text.split()
            time = ' '.join(time[1:4])

            data.append({'text': text,
                         'author': author,
                         'time': time
            })

        return data[:self.config.number]
