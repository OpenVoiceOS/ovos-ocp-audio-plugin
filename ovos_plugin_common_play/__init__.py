from os.path import basename

from mycroft_bus_client import Message
from ovos_plugin_manager.templates.audio import AudioBackend
from ovos_utils.log import LOG
from ovos_workshop.frameworks.playback.status import *
from ovos_workshop.frameworks.playback.utils import extract_metadata


class OVOSCommonPlayAdapterService(AudioBackend):
    """ This plugin makes regular mycroft skills that use the audio service
    go trough the OVOS common play framework, this plugin simply delegates
    the task by emitting bus messages expected by Ovos Common Play API"""

    def __init__(self, config, bus=None, name='ovos.common_play'):
        super(OVOSCommonPlayAdapterService, self).__init__(config=config,
                                                           bus=bus)
        self.name = name
        self.tracks = []
        self._track_info = {}
        self.bus.on("gui.player.media.service.set.meta",
                    self.handle_receive_meta)

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
                        "status": TrackState.DISAMBIGUATION
                        }
            meta["skill_id"] = "ovos.common_play.plugin"
            self.tracks.append(meta)

        self.bus.emit(Message('ovos.common_play.playlist.queue',
                              {"tracks": self.tracks}))
        self.bus.emit(Message('ovos.common_play.media.state',
                              {'state': MediaState.LOADING_MEDIA}))

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


def load_service(base_config, bus):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'ovos_common_play' and
                backends[b].get('active', True)]
    instances = [OVOSCommonPlayAdapterService(s[1], bus, s[0]) for s in
                 services]
    return instances
