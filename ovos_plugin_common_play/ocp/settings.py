from ovos_plugin_common_play.ocp.status import MediaType, PlaybackMode
from ovos_utils.skills.settings import PrivateSettings


class OCPSettings(PrivateSettings):
    # media types that can be safely cast to audio only streams when GUI is
    # not available
    cast2audio = [
        MediaType.MUSIC,
        MediaType.PODCAST,
        MediaType.AUDIOBOOK,
        MediaType.RADIO,
        MediaType.RADIO_THEATRE,
        MediaType.VISUAL_STORY,
        MediaType.NEWS
    ]

    def __init__(self):
        super(OCPSettings, self).__init__("ovos.common_play")

    @property
    def playback_mode(self):
        return self.get("playback_mode", PlaybackMode.AUTO)

    @property
    def early_stop_thresh(self):
        """ early_stop_thresh (int): stop collecting results if we get a
                                   match with confidence >= early_stop_thresh"""
        return self.get("early_stop_thresh", 90)

    @property
    def early_stop_grace_period(self):
        """early_stop_grace_period (float): sleep this amount before early stop,
                                   allows skills that "just miss" to also be
                                   taken into account"""
        return self.get("early_stop_grace_period", 1.0)

    @property
    def backwards_compatibility(self):
        """backwards_compatibility (bool): if True emits the regular
                                            mycroft-core bus messages to get
                                            results from "old style" skills"""
        return self.get("backwards_compatibility", True)

    @property
    def allow_extensions(self):
        """  allow_extensions (bool): if True, allow skills to request more
                                     time, extend min_timeout for specific
                                     queries up to max_timeout"""
        return self.get("allow_extensions", True)

    @property
    def search_fallback(self):
        """ search_fallback (bool): if no results, perform a second query
                                   with MediaType.GENERIC"""
        return self.get("search_fallback", True)

    @property
    def force_audioservice(self):
        return self.get("force_audioservice", False)

    @property
    def autoplay(self):
        return self.get("autoplay", True)

    @property
    def min_timeout(self):
        """min_timeout (float): minimum time to wait for skill replies,
                                 after this time, if at least 1 result was
                                 found, selection is triggered"""
        return self.get("min_timeout", 1)

    @property
    def max_timeout(self):
        """max_timeout (float): maximum time to wait for skill replies,
                                 after this time, regardless of number of
                                 results, selection is triggered"""
        return self.get("max_timeout", 5)

    @property
    def min_score(self):
        return self.get("min_score", 50)

    @property
    def audio_only(self):
        return self.playback_mode == PlaybackMode.AUDIO_ONLY

    @property
    def video_only(self):
        return self.playback_mode == PlaybackMode.VIDEO_ONLY
