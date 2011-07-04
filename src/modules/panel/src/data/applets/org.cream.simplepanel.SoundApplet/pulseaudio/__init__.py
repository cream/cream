import gobject

from _pulseaudio import *

PA_VOLUME_CONVERSION_FACTOR = 655.36

def volume_to_pa_volume(volume):

    vol = pa_cvolume()
    vol.channels = len(volume)
    v = pa_volume_t * 32
    vol.values = v()
    for i in range(0, len(volume)):
        if i == 32: return vol
        channel_volume = volume[i]
        if channel_volume < 0: channel_volume = 0
        if channel_volume > 100: channel_volume = 100
        vol.values[i] = int(channel_volume * PA_VOLUME_CONVERSION_FACTOR)

    return vol

def pa_volume_to_volume(volume):

    vol = []
    for i in range(0, volume.channels):
        vol.append( int(volume.values[i] / PA_VOLUME_CONVERSION_FACTOR) )
    return vol

class PulseAudio(gobject.GObject):

    __gtype_name__ = 'PulseAudio'
    __gsignals__ = {
        'default-sink-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        'sink-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))
        }

    def __init__(self, name):

        gobject.GObject.__init__(self)

        self.name = name
        self.default_sink = None
        self.sinks = {}

        self._mainloop = pa_threaded_mainloop_new()
        self._mainloop_api = pa_threaded_mainloop_get_api(self._mainloop)

        self._context = pa_context_new(self._mainloop_api, self.name)

        self._null_cb = pa_context_success_cb_t(self.null_cb)
        self._context_notify_cb = pa_context_notify_cb_t(self.context_notify_cb)
        self._pa_context_subscribe_cb = pa_context_subscribe_cb_t(self.pa_context_subscribe_cb)
        self._pa_server_info_cb = pa_server_info_cb_t(self.pa_server_info_cb)
        self._pa_sink_info_cb = pa_sink_info_cb_t(self.pa_sink_info_cb)

        pa_context_set_state_callback(self._context, self._context_notify_cb, None)


    def connect(self):

        pa_context_connect(self._context, None, 0, None);
        pa_threaded_mainloop_start(self._mainloop)


    def context_notify_cb(self, context, userdata):

        ctc = pa_context_get_state(context)
        if ctc == PA_CONTEXT_READY:
            pa_context_set_subscribe_callback(self._context, self._pa_context_subscribe_cb, None);
            o = pa_context_subscribe(self._context, (pa_subscription_mask_t)
                                           (PA_SUBSCRIPTION_MASK_SINK |
                                            PA_SUBSCRIPTION_MASK_SOURCE |
                                            PA_SUBSCRIPTION_MASK_SINK_INPUT |
                                            PA_SUBSCRIPTION_MASK_SOURCE_OUTPUT |
                                            PA_SUBSCRIPTION_MASK_CLIENT |
                                            PA_SUBSCRIPTION_MASK_SERVER), self._null_cb, None)
            pa_operation_unref(o)

            o = pa_context_get_server_info(self._context, self._pa_server_info_cb, None)
            pa_operation_unref(o)

            o = pa_context_get_sink_info_list(self._context, self._pa_sink_info_cb, True)
            pa_operation_unref(o)
        elif ctc == PA_CONTEXT_FAILED:
            print "FAILED"
        elif ctc == PA_CONTEXT_TERMINATED:
            print "TERMINATED"


    def null_cb(self, *args):
        pass


    def pa_context_subscribe_cb(self, context, event_type, index, user_data):

        facility = event_type & PA_SUBSCRIPTION_EVENT_FACILITY_MASK
        type = event_type & PA_SUBSCRIPTION_EVENT_TYPE_MASK

        if facility == PA_SUBSCRIPTION_EVENT_SERVER:
            o = pa_context_get_server_info(self._context, self._pa_server_info_cb, None)
            pa_operation_unref(o)
        elif facility == PA_SUBSCRIPTION_EVENT_SINK:
            if type == PA_SUBSCRIPTION_EVENT_REMOVE:
                self.sinks = {}
            o = pa_context_get_sink_info_list(self._context, self._pa_sink_info_cb, None)
            pa_operation_unref(o)


    def pa_server_info_cb(self, context, server_info, userdata):

        if server_info:
            self.default_sink = server_info.contents.default_sink_name
            gobject.idle_add(lambda: self.emit('default-sink-changed', self.default_sink))


    def pa_sink_info_cb(self, context, sink_info, index, userdata):

        if not sink_info:
            return

        sink_info = sink_info.contents

        name = sink_info.name
        description = sink_info.description
        volume = pa_volume_to_volume(sink_info.volume)
        if sink_info.mute == 1:
            mute = True
        else:
            mute = False

        self.sinks[name] = {
            'description': description,
            'volume': volume,
            'mute': mute
            }

        gobject.idle_add(lambda: self.emit('sink-changed', name))


    def get_sinks(self):
        return self.sinks


    def set_default_sink(self, sink):

        o = pa_context_set_default_sink(self._context, sink, self._null_cb, None)
        pa_operation_unref(o)


    def get_default_sink(self):
        return self.default_sink


    def set_volume(self, volume, sink=None):

        vol = volume_to_pa_volume(volume)

        o = pa_context_set_sink_volume_by_name(self._context, sink or self.default_sink, vol, self._null_cb, None)
        pa_operation_unref(o)


    def get_volume(self, sink=None):
        return self.sinks[sink or self.default_sink]['volume']


    def set_mute(self, mute, sink=None):

        o = pa_context_set_sink_mute_by_name(self._context, sink or self.default_sink, int(mute), self._null_cb, None)
        pa_operation_unref(o)


    def get_mute(self, sink=None):
        return self.sinks[sink or self.default_sink]['mute']
