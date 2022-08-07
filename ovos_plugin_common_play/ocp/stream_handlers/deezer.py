from os import makedirs
from os.path import join
from tempfile import gettempdir

from ovos_utils.log import LOG
from ovos_ocp_deezer_plugin import OCPDeezerExtractor


def get_deezer_audio_stream(url, deezer=None, path=None):
    extractor = OCPDeezerExtractor(deezer)
    return extractor.get_deezer_audio_stream(url, path)


def is_deezer(url):
    return OCPDeezerExtractor.is_deezer(url)
