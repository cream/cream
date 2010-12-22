import os
from coverart.utils import generate_url, download_file, md5, filename_for_album
from coverart import config

class NotFound(Exception):
    pass

class AbstractBackend(object):
    def download_cover(self, artist, album):
        raise NotImplementedError()

class LastFmBackend(AbstractBackend):
    BASE_URL = 'http://ws.audioscrobbler.com/2.0/'

    @classmethod
    def download_cover(cls, artist, album):
        import lxml.etree
        url = generate_url(
            cls.BASE_URL, method='album.search',
            api_key=config.LASTFM_API_KEY,
            album=album
        )
        xml = lxml.etree.parse(url).getroot()

        best_match = None
        for match in xml.find('results/albummatches'):
            album_artist = match.findtext('artist')
            if album_artist.lower() == artist.lower():
                best_match = match
                break
            if best_match is None:
                best_match = match
        if best_match is None:
            raise NotFound()
        return download_file(
            best_match.findall('image')[-1].text, # last = largest
            filename_for_album(
                best_match.find('artist').text,
                album
            )
        )
