import os
from backends import AbstractBackend, NotFound
from utils import filename_for_album

def get_cover(artist, album):
    path = filename_for_album(artist, album)
    if os.path.exists(path):
        return path
    else:
        for backend in AbstractBackend.__subclasses__():
            try:
                return backend.download_cover(artist, album)
            except NotFound:
                pass
        raise NotFound

def get_async(artist, album, callback):
    import threading
    class _Thread(threading.Thread):
        def run(self):
            callback(artist, album, get_cover(artist, album))
    thread = _Thread()
    thread.start()
    return thread

if __name__ == '__main__':
    def callback(artist, album, cover_path):
        print "Got cover art for", artist, album
        print "Cover is at", cover_path

    get_async("Insomnium", "Above The Weeping World", callback)
