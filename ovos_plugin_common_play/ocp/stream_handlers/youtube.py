import enum
import json

import requests
from ovos_utils.log import LOG
from ovos_ocp_youtube_plugin import YoutubeBackend, YdlBackend, YoutubeLiveBackend, OCPYoutubeExtractor


def get_youtube_live_from_channel(url, ocp_settings=None):
    extractor = OCPYoutubeExtractor(ocp_settings)
    return extractor.get_youtube_live_from_channel(url)


def get_youtube_stream(url,
                       audio_only=False,
                       ocp_settings=None):
    extractor = OCPYoutubeExtractor(ocp_settings)
    return extractor.extract_stream(url)


def is_youtube(url):
    extractor = OCPYoutubeExtractor()
    return extractor.is_youtube(url)


def get_invidious_stream(url, audio_only=False, ocp_settings=None):
    # proxy via invidious instance
    # public instances: https://docs.invidious.io/Invidious-Instances.md
    # self host: https://github.com/iv-org/invidious
    extractor = OCPYoutubeExtractor(ocp_settings)
    return extractor.get_invidious_stream(url, audio_only)


def get_ydl_stream(url, audio_only=False, ocp_settings=None,
                   *args, **kwargs):
    extractor = OCPYoutubeExtractor(ocp_settings)
    return extractor.get_ydl_stream(url, audio_only, *args, **kwargs)


def get_pafy_stream(url, audio_only=False, ocp_settings=None):
    extractor = OCPYoutubeExtractor(ocp_settings)
    return extractor.get_pafy_stream(url, audio_only)


def get_pytube_stream(url, audio_only=False, ocp_settings=None, *args, **kwargs):
    extractor = OCPYoutubeExtractor(ocp_settings)
    return extractor.get_pytube_stream(url, audio_only, *args, **kwargs)


def get_pytube_channel_livestreams(url, ocp_settings=None):
    extractor = OCPYoutubeExtractor(ocp_settings)
    return extractor.get_pytube_channel_livestreams(url)


def get_youtubesearcher_channel_livestreams(url, ocp_settings=None):
    extractor = OCPYoutubeExtractor(ocp_settings)
    return extractor.get_youtubesearcher_channel_livestreams(url)


def get_youtube_live_from_channel_redirect(url, ocp_settings=None):
    extractor = OCPYoutubeExtractor(ocp_settings)
    return extractor.get_youtube_live_from_channel_redirect(url)
