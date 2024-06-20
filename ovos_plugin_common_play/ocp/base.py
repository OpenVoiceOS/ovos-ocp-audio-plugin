from os.path import join, isfile

from ovos_bus_client.message import Message
from ovos_config.locations import get_xdg_config_save_path
from ovos_plugin_manager.templates.audio import AudioBackend
from ovos_utils.log import LOG
from ovos_workshop.decorators.ocp import MediaState, PlayerState, TrackState

from ovos_plugin_common_play.ocp.constants import OCP_ID
from ovos_plugin_common_play.ocp.utils import extract_metadata


class OCPAbstractComponent:
    def __init__(self, player=None):
        """
        player: OCPInterface
        """
        self._player = None
        if player:
            self.bind(player)

    def bind(self, player):
        self._player = player

    @property
    def player(self):
        return self._player

    @property
    def settings(self):
        if self._player:
            return self._player.settings

        default_path = join(get_xdg_config_save_path(), 'apps',
                            OCP_ID, 'settings.json')
        if isfile(default_path):
            from json_database import JsonStorage
            return JsonStorage(default_path, disable_lock=True)
        return dict()

    @property
    def enclosure(self):
        if not self._player:
            return None
        return self._player.enclosure

    @property
    def gui(self):
        if not self._player:
            return None
        return self._player.gui

    @property
    def bus(self):
        if not self._player:
            return None
        return self._player.bus

    def add_event(self, msg_type, handler):
        self.player.add_event(msg_type, handler)

    def remove_event(self, msg_type):
        self.player.remove_event(msg_type)


class OCPAudioPlayerBackend(AudioBackend):
    """Base class for all OCP audio backend implementations.

    In OVOS audio backends are single-track, playlists are handled by OCP
    This base class introduces some helper methods for reporting status to OCP
    and adds a compat layer to all playlist related handlers

    see the VLC plugin for an implementation example
    https://github.com/OpenVoiceOS/ovos-vlc-plugin

       Arguments:
           config (dict): configuration dict for the instance
           bus (MessageBusClient): Mycroft messagebus emitter
       """

    def __init__(self, config=None, bus=None):
        super().__init__(config, bus)
        self._now_playing = None  # single uri
        self._tracks = []  # list of dicts for OCP entries

    def load_track(self, uri):
        """ This method is only used by ovos-core
        In ovos audio backends are single-track, playlists are handled by OCP
        """
        self._now_playing = uri
        LOG.debug(f"queuing for {self.__class__.__name__} playback: {uri}")
        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": MediaState.LOADED_MEDIA}))
        self.bus.emit(Message("ovos.common_play.track.state", {
            "state": TrackState.QUEUED_AUDIOSERVICE
        }))

    def ocp_start(self):
        """Emit OCP status events for play"""
        self.bus.emit(Message("ovos.common_play.player.state",
                              {"state": PlayerState.PLAYING}))
        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": MediaState.LOADED_MEDIA}))
        self.bus.emit(Message("ovos.common_play.track.state",
                              {"state": TrackState.PLAYING_AUDIOSERVICE}))

    def ocp_error(self):
        """Emit OCP status events for playback error"""
        if self._now_playing:
            self.bus.emit(Message("ovos.common_play.media.state",
                                  {"state": MediaState.INVALID_MEDIA}))
            self._now_playing = None

    def ocp_stop(self):
        """Emit OCP status events for stop"""
        if self._now_playing:
            self._now_playing = None
            self.bus.emit(Message("ovos.common_play.player.state",
                                  {"state": PlayerState.STOPPED}))
            self.bus.emit(Message("ovos.common_play.media.state",
                                  {"state": MediaState.END_OF_MEDIA}))

    def ocp_pause(self):
        """Emit OCP status events for pause"""
        if self._now_playing:
            self.bus.emit(Message("ovos.common_play.player.state",
                                  {"state": PlayerState.PAUSED}))

    def ocp_resume(self):
        """Emit OCP status events for resume"""
        if self._now_playing:
            self.bus.emit(Message("ovos.common_play.player.state",
                                  {"state": PlayerState.PLAYING}))
            self.bus.emit(Message("ovos.common_play.track.state",
                                  {"state": TrackState.PLAYING_AUDIOSERVICE}))

    # Mycroft-core backwards compat
    # handlers below should not be triggered at all under ovos-core
    # but they will if running under mycroft-core
    # or if some 3rd party is sending bus messages directly
    # this serves as a compat layer sending equivalent OCP messages
    # see https://github.com/OpenVoiceOS/ovos-core/pull/181
    def next(self):
        """Skip to next track in playlist.
        Track start is handled by OCP
        subclasses should cleanup currently playing audio and send "ovos.common_play.next"
        """
        self.stop()
        self.bus.emit(Message("ovos.common_play.next"))

    def previous(self):
        """Skip to previous track in playlist.
        Track start is handled by OCP
        subclasses should cleanup currently playing audio and send "ovos.common_play.previous"
        """
        self.stop()
        self.bus.emit(Message("ovos.common_play.previous"))

    def seek_forward(self, seconds=1):
        """Skip X seconds.

        Arguments:
            seconds (int): number of seconds to seek, if negative rewind
        """
        miliseconds = seconds * 1000
        new_pos = self.get_track_position() + miliseconds
        self.set_track_position(new_pos)

    def seek_backward(self, seconds=1):
        """Rewind X seconds.

        Arguments:
            seconds (int): number of seconds to seek, if negative jump forward.
        """
        miliseconds = seconds * 1000
        new_pos = self.get_track_position() - miliseconds
        self.set_track_position(new_pos)

    def lower_volume(self):
        """Lower volume.

        This method is used to implement audio ducking. It will be called when
        Mycroft is listening or speaking to make sure the media playing isn't
        interfering.

        This is only here for backward compat, subclasses should not change this
        This will forward a old style audio service message to OCP
        """
        if self.config.get("duck", False):
            self.bus.emit(Message("ovos.common_play.duck"))

    def restore_volume(self):
        """Restore normal volume.

        Called when to restore the playback volume to previous level after
        Mycroft has lowered it using lower_volume().

        This is only here for backward compat, subclasses should not change this
        This will forward a old style audio service message to OCP
        """
        if self.config.get("duck", False):
            self.bus.emit(Message("ovos.common_play.unduck"))

    def clear_list(self):
        """Clear playlist.
        This is only here for backward compat, subclasses should not change this
        This will forward a old style audio service message to OCP"""
        self._tracks = []
        self.bus.emit(Message("ovos.common_play.playlist.clear"))

    def add_list(self, tracks):
        """Add tracks to backend's playlist.

        This is only here for backward compat, subclasses should not change this
        This will forward a old style audio service message to OCP

        Arguments:
            tracks (list): list of tracks.
        """
        if isinstance(tracks, (str, tuple)):
            tracks = [tracks]
        elif not isinstance(tracks, list):
            raise ValueError
        self.load_track(tracks[0])
        self._tracks = [extract_metadata(t) for t in tracks]
        self.bus.emit(Message('ovos.common_play.playlist.queue',
                              {'tracks': self._tracks}))
        self.track_info()  # will trigger update in track data
