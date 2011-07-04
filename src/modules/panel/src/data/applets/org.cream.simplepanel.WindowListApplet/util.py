#!/usr/bin/env python

import gtk

ICON_SIZE = 32
MIN_DIM = 16

def convert_icon(data, desired_size=ICON_SIZE):
    length = len(data)
    if length < (MIN_DIM * MIN_DIM + 2):
        raise IconError('Icon too small: Expected %d, got %d' % (MIN_DIM * MIN_DIM + 2, length))
    sizes = {}
    start = 0
    while start < length:
        width = data[start]
        height = data[start + 1]
        if width != height:
            start += 2 + width * height
            continue
        rgba_data = ''
        for argb in data[start + 2:start + 2 + width*height]:
            rgba = ((argb << 8) & 0xffffff00) | (argb >> 24)
            rgba_data += chr(rgba >> 24)
            rgba_data += chr((rgba >> 16) & 0xff)
            rgba_data += chr((rgba >> 8) & 0xff)
            rgba_data += chr(rgba & 0xff)
        start += 2 + width * height
        sizes[width] = gtk.gdk.pixbuf_new_from_data(rgba_data, gtk.gdk.COLORSPACE_RGB, True, 8, width, height, width * 4)
    use_pb = None
    biggest = None
    for size, pb in sizes.iteritems():
        if (biggest is None or biggest.get_width() < pb.get_width()):
            biggest = pb
        if size >= desired_size:
            use_pb = pb
    if not sizes:
        return None
    if (use_pb is None or use_pb.get_width() != desired_size):
        use_pb = biggest.scale_simple(desired_size, desired_size, gtk.gdk.INTERP_HYPER)
    return use_pb
