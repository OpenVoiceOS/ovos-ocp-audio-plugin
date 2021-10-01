import mimetypes

from ovos_plugin_common_play.ocp.stream_handlers.deezer import *
from ovos_plugin_common_play.ocp.stream_handlers.rssfeeds import *
from ovos_plugin_common_play.ocp.stream_handlers.soundcloud import *
from ovos_plugin_common_play.ocp.stream_handlers.youtube import *
from ovos_plugin_common_play.ocp.stream_handlers.bandcamp import *


def find_mime(uri):
    """ Determine mime type. """
    mime = mimetypes.guess_type(uri)
    if mime:
        return mime
    else:
        return None


def available_extractors():
    ext = ["/", "http"]
    try:
        import deezeridu
        ext.append("deezer//")
    except:
        pass
    try:
        import feedparser
        ext.append("rss//")
    except:
        pass
    try:
        # TODO deprecate need in favor of youtube-dl ?
        import pafy
        ext.append("youtube//")
    except:
        pass
    try:
        import youtube_dl
        ext.append("soundcloud//")
    except:
        pass
    try:
        import youtube_searcher
        ext.append("youtube.channel.live//")
    except:
        pass
    try:
        import py_bandcamp
        ext.append("bandcamp//")
    except:
        pass
    return ext
