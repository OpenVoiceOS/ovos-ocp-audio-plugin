import mimetypes

from ovos_plugin_common_play.ocp.stream_handlers.deezer import *
from ovos_plugin_common_play.ocp.stream_handlers.rssfeeds import *
from ovos_plugin_common_play.ocp.stream_handlers.soundcloud import *
from ovos_plugin_common_play.ocp.stream_handlers.youtube import *


def find_mime(uri):
    """ Determine mime type. """
    mime = mimetypes.guess_type(uri)
    if mime:
        return mime
    else:
        return None
