from ovos_plugin_common_play.ocp.stream_handlers.youtube import \
    get_ydl_stream, YdlBackend
import enum
from ovos_ocp_bandcamp_plugin import OCPBandcampExtractor


class BandcampBackend(str, enum.Enum):
    YDL = "youtube-dl"
    PYBANDCAMP = "pybandcamp"


def get_bandcamp_audio_stream(url, backend=BandcampBackend.PYBANDCAMP,
                              fallback=True, ydl_backend=YdlBackend.YDLP):
    return OCPBandcampExtractor().extract_stream(url)


def get_pybandcamp_stream(url):
    return OCPBandcampExtractor().extract_stream(url)


def is_bandcamp(url):
    return OCPBandcampExtractor.is_bandcamp(url)
