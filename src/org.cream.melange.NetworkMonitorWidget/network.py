from time import time

class Bytes(float):

    def __new__(cls, val):
        return float.__new__(cls, val)

    def __sub__(self, other):
        return Bytes(float.__sub__(self, other))

    def __div__(self, other):
        return Bytes(float.__div__(self, other))

    @property
    def kib(self):
        return self / 1024

    @property
    def mib(self):
        return self / 1024 ** 2

class Traffic(object):

    def __init__(self, interface, download, upload):
        self.interface = interface
        self.download = download
        self.upload = upload

    def __sub__(self, other):
        download_delta = self.download - other.download
        upload_delta = self.upload - other.upload
        return (download_delta, upload_delta)

class NetworkMonitor(object):

    def __init__(self, interface):
        self.interface = interface

        self.download_total = 0
        self.upload_total = 0
        self.download_per_sec = 0
        self.upload_per_sec = 0

        self.last_updated = time()
        self.traffic = Traffic(interface, 0, 0)

    def _parse_traffic(self):
        with open('/proc/net/dev', 'r') as file_:
            interfaces = file_.readlines()[2:] #ignore header

        for interface in interfaces:
            interface = interface.split()
            name, download = interface[:2]
            upload = interface[9]
            name = name.replace(':', '')

            if name == self.interface:
                return Traffic(name, Bytes(download), Bytes(upload))

    def update(self):
        traffic = self._parse_traffic()
        now = time()

        download_delta, upload_delta = traffic - self.traffic
        time_delta = now - self.last_updated

        self.download_total = traffic.download
        self.upload_total = traffic.upload
        self.download_per_sec = download_delta / time_delta
        self.upload_per_sec = upload_delta / time_delta

        self.traffic = traffic
        self.last_updated = now
