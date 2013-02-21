import os
import urllib2
import hashlib
import config

def md5(*stuff):
    s = u''.join(stuff)
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def generate_url(base, **kwargs):
    return base.rstrip(u'?') + u'?' \
           + u'&'.join(u'{0}={1}'.format(*item)
                      for item in kwargs.iteritems())

def download_file(url, destination):
    sock = urllib2.urlopen(url)
    with open(destination, 'w') as fileobj:
        for chunk in read_chunked(sock):
            fileobj.write(chunk)
    return destination

def read_chunked(fileobj, chunk_size=8*1024):
    chunk = fileobj.read(chunk_size)
    while chunk:
        yield chunk
        chunk = fileobj.read(chunk_size)

def filename_for_album(artist, album):
    return os.path.join(
        config.COVER_ART_BASE_DIR,
        u'album-%s.jpg' % md5(artist, album)
    )

