"""
Compatibility module for imghdr (removed in Python 3.13)
"""
import struct
import os

def what(file, h=None):
    if h is None:
        if isinstance(file, str):
            with open(file, 'rb') as f:
                h = f.read(32)
        else:
            location = file.tell()
            h = file.read(32)
            file.seek(location)
    
    if not h:
        return None
    
    if h.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    elif h.startswith(b'\xff\xd8'):
        return 'jpeg'
    elif h.startswith(b'GIF8'):
        return 'gif'
    elif h.startswith(b'BM'):
        return 'bmp'
    elif h.startswith(b'RIFF') and h[8:12] == b'WEBP':
        return 'webp'
    elif h.startswith(b'\x00\x00\x01\x00'):
        return 'ico'
    elif h.startswith(b'\x00\x00\x02\x00'):
        return 'cur'
    elif h.startswith(b'II*\x00') or h.startswith(b'MM\x00*'):
        return 'tiff'
    
    return None