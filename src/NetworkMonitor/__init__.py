#! /usr/bin/env python
# -*- coding: utf-8 -*-

from network import NetworkMonitor as _NetworkMonitor

from cream.contrib.melange import api

@api.register('networkmonitor')
class NetworkMonitor(api.API):

    def __init__(self):
    
        api.API.__init__(self)
        
        self.network_monitor = _NetworkMonitor('eth0')
        self.network_monitor.update()
        
    @api.expose
    def get_data(self):
        self.network_monitor.update()

        return {
            'download': round(self.network_monitor.download_total.mib, 1),
            'upload': round(self.network_monitor.upload_total.mib, 1),
            'download_per_sec': int(self.network_monitor.download_per_sec.kib),
            'upload_per_sec': int(self.network_monitor.upload_per_sec.kib)
        }
