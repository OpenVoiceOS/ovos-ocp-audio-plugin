from os.path import basename
from pprint import pformat

from mycroft_bus_client import Message
from ovos_plugin_manager.templates.audio import AudioBackend
from ovos_utils.log import LOG

from ovos_plugin_common_play.ocp import OCP, OCPSettings
from ovos_plugin_common_play.ocp.status import *
from ovos_plugin_common_play.ocp.utils import extract_metadata


class OCPAudioBackend(AudioBackend):
    """ This plugin makes regular mycroft skills that use the audio service
    go trough the OVOS common play framework, this plugin simply delegates
    the task by emitting bus messages expected by Ovos Common Play API. If
    configured it will also launch OCP itself """

    def __init__(self, config, bus=None, name='ovos.common_play'):
        super(OCPAudioBackend, self).__init__(config=config,
                                              bus=bus)
        self.name = name
        self.tracks = []
        self._track_info = {}
        self.bus.on("gui.player.media.service.set.meta",
                    self.handle_receive_meta)
        self.create_ocp(config)

    def create_ocp(self, config):
        mode = config.get("mode", "auto")
        ocp_settings = OCPSettings()
        ocp_settings.update(config)

        LOG.debug(f"OCP settings:\n {pformat(ocp_settings)}")

        if mode == "external":
            # flag for external OCP, eg, system service daemon
            # send only bus messages and dont create ocp object
            self.ocp = None
        elif mode == "auto":
            # if OCP is already running connect to it, else launch it
            if not self.bus.wait_for_response(Message("ovos.common_play.ping"),
                                              "ovos.common_play.pong"):
                try:
                    self.ocp = OCP(bus=self.bus, settings=ocp_settings)
                except Exception as e:
                    # otherwise stack trace is swallowed by plugin loader
                    LOG.exception(e)
                    raise
        else:
            try:
                self.ocp = OCP(bus=self.bus, settings=ocp_settings)
            except Exception as e:
                # otherwise stack trace is swallowed by plugin loader
                LOG.exception(e)
                raise

    def handle_receive_meta(self, message):
        self._track_info = message.data

    def supported_uris(self):
        return ['file', 'http', 'https']

    def clear_list(self):
        self.tracks = []
        self.bus.emit(Message('ovos.common_play.playlist.clear'))

    def add_list(self, tracks):
        self.tracks = []
        for t in tracks:
            try:
                # only works for local files
                # audio only (?)
                meta = extract_metadata(t)
            except Exception as e:
                LOG.exception(e)
                # TODO let's try to dig for message and see if theres
                #  anything there, maybe set title / artist to skill_id ?
                meta = {"uri": t,
                        "title": basename(t),
                        "artist": "ovos.common_play.plugin",
                        "album": "",
                        "image": "",
                        "playback": PlaybackType.AUDIO,  # TODO mime type check
                        "status": TrackState.QUEUED_AUDIO
                        }
            meta["skill_id"] = "ovos.common_play.plugin"
            self.tracks.append(meta)

        self.bus.emit(Message('ovos.common_play.playlist.queue',
                              {"tracks": self.tracks}))

    def play(self, repeat=False):
        """ Play media playback. """
        if len(self.tracks):
            self._track_info = self.tracks[0]
            self.bus.emit(Message('ovos.common_play.play',
                                  {'repeat': repeat,
                                   "media": self.tracks[0],
                                   "playlist": self.tracks}))

    def stop(self):
        """ Stop media playback. """
        self.bus.emit(Message("ovos.common_play.stop"))

    def pause(self):
        """ Pause media playback. """
        self.bus.emit(Message("ovos.common_play.pause"))

    def resume(self):
        """ Resume paused playback. """
        self.bus.emit(Message("ovos.common_play.resume"))

    def next(self):
        """ Skip to next track in playlist. """
        self.bus.emit(Message("ovos.common_play.next"))

    def previous(self):
        """ Skip to previous track in playlist. """
        self.bus.emit(Message("ovos.common_play.previous"))

    def lower_volume(self):
        if self.config.get("duck", False):
            self.bus.emit(Message("ovos.common_play.duck"))

    def restore_volume(self):
        if self.config.get("duck", False):
            self.bus.emit(Message("ovos.common_play.unduck"))

    def track_info(self):
        """
            Fetch info about current playing track.
            Returns:
                Dict with track info.
        """
        return self._track_info

    def shutdown(self):
        self.bus.remove("gui.player.media.service.set.meta",
                        self.handle_receive_meta)
        if self.ocp is not None:
            self.ocp.shutdown()


def load_service(base_config, bus):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'ovos_common_play' and
                backends[b].get('active', True)]
    instances = [OCPAudioBackend(s[1], bus, s[0]) for s in
                 services]
    return instances


OCPPluginConfig = {
    "local": {
        "type": "ovos_common_play",
        "active": True,
        # all values below are optional

        # DBUS
        ## dbus type for MPRIS, "session" or "system"
        "dbus_type": "session",
        ## allow OCP to control MPRIS enabled 3rd party applications
        ## voice enable them (next/prev/stop/resume..)
        ## and stop them when OCP starts it's own playback
        ## NOTE: OCP can be controlled itself via MPRIS independentely of this setting
        "manage_external_players": False,

        # Playback settings
        ## AUTO = 0 - play each entry as considered appropriate,
        ##            ie, make it happen the best way possible
        ## AUDIO_ONLY = 10  - only consider audio entries
        ## VIDEO_ONLY = 20  - only consider video entries
        ## FORCE_AUDIO = 30 - cast video to audio unconditionally
        ##                   (audio can still play in mycroft-gui)
        ## FORCE_AUDIOSERVICE = 40 - cast everything to audio service backend,
        ##                           mycroft-gui will not be used
        ## EVENTS_ONLY = 50 - only emit ocp events,
        ##                    do not display or play anything.
        ##                    allows integration with external interfaces
        "playback_mode": 0,

        ## when media playback ends "click next"
        "autoplay": True,
        ## if True behaves as if the search results are part of the playlist
        ##  eg:
        ##   - click next in last track -> play next search result
        ##   - end of playlist + autoplay -> play next search result
        "merge_search": True,

        # search params
        ## minimum time to wait for skill replies,
        # after this time, if at least 1 result was
        # found, selection is triggered
        "min_timeout": 5,
        ## maximum time to wait for skill replies,
        ## after this time, regardless of number of
        ## results, selection is triggered
        "max_timeout": 15,
        ## ignore results below min_Score
        "min_score": 50,
        ## stop collecting results if we get a
        ## match with confidence >= early_stop_thresh
        "early_stop_thresh": 85,
        ## sleep this amount before early stop,
        ## allows skills that "just miss" to also be taken into account
        "early_stop_grace_period": 0.5,
        ## if True emits the regular mycroft-core
        ## bus messages to get results from "old style" skills
        "backwards_compatibility": True,
        ## allow skills to request more time,
        ## extends min_timeout for individual queries (up to max_timeout)
        "allow_extensions": True,
        ## if no results for a MediaType, perform a second query with MediaType.GENERIC
        "search_fallback": True,

        # stream extractor settings
        ## how to handle bandcamp streams
        ## "pybandcamp", "youtube-dl"
        "bandcamp_backend": "pybandcamp",
        ## how to handle youtube streams
        ## "youtube-dl", "pytube", "pafy", "invidious"
        "youtube_backend": "invidious",
        ## the url to the invidious instance to be used"
        ## by default uses a random instance
        "invidious_host": None,
        ## get final stream locally or from where invidious is hosted
        ## This partially allows bypassing geoblocked content,
        ## but it is a global flag, not per entry.
        "invidious_proxy": False,
        ## different forks of youtube-dl are supported
        ## "yt-dlp", "youtube-dl", "youtube-dlc"
        "ydl_backend": "yt-dlp",
        ## how to extract live streams from a youtube channel
        ## "pytube", "youtube_searcher", "redirect", "youtube-dl"
        "youtube_live_backend": "redirect"  # uses youtube auto redirect https://www.youtube.com/{channel_name}/live
    }
}
