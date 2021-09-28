from ovos_workshop.ocp.stream_handlers.youtube import *
from ovos_workshop.ocp.stream_handlers.deezer import *
from ovos_workshop.ocp.stream_handlers.rssfeeds import *
from ovos_workshop.ocp.stream_handlers.soundcloud import *


import mimetypes


def find_mime(uri):
    """ Determine mime type. """
    mime = mimetypes.guess_type(uri)
    if mime:
        return mime
    else:
        return None
