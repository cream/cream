import json
import base64
import urllib2
from urllib import urlencode
from urlparse import urlsplit

from melange import api

IMGUR_UPLOAD_URL = 'http://imgur.com/api/upload.json'
API_KEY = '97afbe8e4bd793012c847f0f39df8ffe'


class Imgur(object):

    def __init__(self, api_key):

        self.api_key = api_key


    def upload(self, path):

        with open(path, 'rb') as file_handle:
            image = file_handle.read()

        data = {
            'key': self.api_key,
            'image': base64.b64encode(image),
            'path': path
        }

        request = urllib2.Request(IMGUR_UPLOAD_URL, urlencode(data))
        u = urllib2.urlopen(request)
        data = json.loads(u.read())

        return data


@api.register('org.cream.melange.ImgurWidget')
class ImgurWidget(api.API):

    def __init__(self):

        api.API.__init__(self)

        self.imgur = Imgur(API_KEY)

    @api.expose
    def upload(self, path):

        path = urlsplit(path).path
        data = self.imgur.upload(path)

        return data['rsp']['image']['imgur_page']
