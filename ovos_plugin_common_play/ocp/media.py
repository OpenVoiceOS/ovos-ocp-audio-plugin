from os.path import join, dirname
from typing import Union
from dataclasses import dataclass
from ovos_bus_client.client import MessageBusClient
from ovos_bus_client.message import Message
from ovos_utils.json_helper import merge_dict
from ovos_utils.log import LOG
from ovos_workshop.backwards_compat import MediaState, TrackState, PlaybackType, MediaType, Playlist, PluginStream, MediaEntry as _ME

from ovos_plugin_common_play.ocp.constants import OCP_ID
from ovos_plugin_common_play.ocp.utils import ocp_plugins


@dataclass
class MediaEntry(_ME):
    uri: str = ""
    title: str = ""
    artist: str = ""
    match_confidence: int = 0  # 0 - 100
    skill_id: str = OCP_ID
    playback: PlaybackType = PlaybackType.UNDEFINED
    status: TrackState = TrackState.DISAMBIGUATION
    media_type: MediaType = MediaType.GENERIC
    length: int = 0  # in seconds
    image: str = ""
    skill_icon: str = ""
    javascript: str = ""  # to execute once webview is loaded

    def __init__(self, title="", uri="", skill_id=OCP_ID,
                 image=None, match_confidence=0,
                 playback=PlaybackType.UNDEFINED,
                 status=TrackState.DISAMBIGUATION, phrase=None,
                 position=0, length=0, bg_image=None, skill_icon=None,
                 artist=None, is_cps=False, cps_data=None, javascript="",
                 **kwargs):
        uri = uri or ""
        super().__init__(
            title=title,
            match_confidence=match_confidence,
            playback=PlaybackType(playback) if isinstance(playback, int) else playback,
            status=status,
            length=length,
            image=image or join(dirname(__file__), "res/ui/images/ocp_bg.png"),
            skill_icon=skill_icon or join(dirname(__file__), "res/ui/images/ocp.png"),
            javascript=javascript,
            uri=f'file://{uri}' if uri.startswith('/') else uri,
            skill_id=skill_id,
            media_type=kwargs.get("media_type") or MediaType.GENERIC
        )
        self.artist = artist
        self.position = position
        self.phrase = phrase
        self.bg_image = bg_image or join(dirname(__file__), "res/ui/images/ocp_bg.png")
        self.is_cps = is_cps
        self.data = kwargs
        self.cps_data = cps_data or {}

    @property
    def info(self) -> dict:
        """
        Return a dict representation of this MediaEntry + infocard for QML model
        """
        return merge_dict(self.as_dict, self.infocard)

    @staticmethod
    def from_dict(track: dict) -> 'MediaEntry':
        if "uri" not in track:  # not valid in ovos-utils.ocp
            track["uri"] = ""
        return _ME.from_dict(track)


@dataclass
class NowPlaying(MediaEntry):
    uri: str = ""
    title: str = ""
    artist: str = ""
    match_confidence: int = 0  # 0 - 100
    skill_id: str = OCP_ID
    playback: PlaybackType = PlaybackType.UNDEFINED
    status: TrackState = TrackState.DISAMBIGUATION
    media_type: MediaType = MediaType.GENERIC
    length: int = 0  # in seconds
    image: str = ""
    skill_icon: str = ""
    javascript: str = ""  # to execute once webview is loaded

    def __init__(self, *args, **kwargs):
        MediaEntry.__init__(self, *args, **kwargs)
        self._player = None

    @property
    def as_dict(self) -> dict:
        """
        Return a dict representation of this MediaEntry
        """
        return {k: v for k, v in self.__dict__.items()
                if not k.startswith("_")}

    @property
    def bus(self) -> MessageBusClient:
        """
        Return the MessageBusClient inherited from the bound OCPMediaPlayer
        """
        return self._player.bus

    @property
    def _settings(self) -> dict:
        """
        Return the dict settings inherited from the bound OCPMediaPlayer
        """
        return self._player.settings

    def as_entry(self) -> MediaEntry:
        """
        Return a MediaEntry representation of this object
        """
        return MediaEntry.from_dict(self.as_dict)

    def bind(self, player):
        """
        Bind an OCPMediaPlayer object to this NowPlaying instance. Registers
        messagebus event handlers and defines `self._player`
        @param player: OCPMediaPlayer instance to bind
        """
        # needs to start with _ to avoid json serialization errors
        self._player = player
        self._player.add_event("ovos.common_play.track.state",
                               self.handle_track_state_change)
        self._player.add_event("ovos.common_play.media.state",
                               self.handle_media_state_change)
        self._player.add_event("ovos.common_play.play",
                               self.handle_external_play)
        self._player.add_event("ovos.common_play.playback_time",
                               self.handle_sync_seekbar)
        self._player.add_event('gui.player.media.service.get.meta',
                               self.handle_player_metadata_request)
        self._player.add_event('mycroft.audio.service.track_info_reply',
                               self.handle_sync_trackinfo)
        self._player.add_event('mycroft.audio.service.play',
                               self.handle_audio_service_play)
        self._player.add_event('mycroft.audio.playing_track',
                               self.handle_audio_service_play_start)

    def shutdown(self):
        """
        Remove NowPlaying events from the MessageBusClient
        """
        self._player.remove_event("ovos.common_play.track.state")
        self._player.remove_event("ovos.common_play.playback_time")
        self._player.remove_event('gui.player.media.service.get.meta')
        self._player.remove_event('mycroft.audio_only.service.track_info_reply')

    def reset(self):
        """
        Reset the NowPlaying MediaEntry to default parameters
        """
        LOG.debug("Resetting NowPlaying")
        self.title = ""
        self.artist = None
        self.skill_icon = None
        self.skill_id = None
        self.position = 0
        self.length = None
        self.is_cps = False
        self.cps_data = {}
        self.data = {}
        self.phrase = None
        self.javascript = ""
        self.playback = PlaybackType.UNDEFINED
        self.status = TrackState.DISAMBIGUATION

    def update(self, entry: Union[dict, MediaEntry], skipkeys: list = None, newonly: bool = False):
        """
        Update this MediaEntry and emit `gui.player.media.service.set.meta`
        @param entry: dict or MediaEntry object to update this object with
        @param skipkeys: list of keys to not change
        @param newonly: if True, only adds new keys; existing keys are unchanged
        """
        if isinstance(entry, _ME):
            entry = entry.as_dict
        super().update(entry, skipkeys, newonly)
        # uri updates should not be skipped
        if newonly and entry.get("uri"):
            super().update({"uri": entry["uri"]})
        # sync with gui media player on track change
        if not self._player:
            LOG.error("Instance not bound! Call `bind` before trying to use "
                      "the messagebus.")
            return
        self.bus.emit(Message("gui.player.media.service.set.meta",
                              {"title": self.title,
                               "image": self.image,
                               "artist": self.artist}))

    def extract_stream(self):
        """
        update missing metadata via OCP plugins that can parse the URI
        this can include a playable stream (eg, youtube urls) or just track data (name, artist, icon...)
        """
        uri = self.uri
        if not uri:
            raise ValueError("No URI to extract stream from")
        video = self.playback == PlaybackType.VIDEO
        meta = ocp_plugins().extract_stream(uri, video)
        # update media entry with new data
        if meta:
            LOG.info(f"OCP plugins metadata: {meta}")
            self.update(meta, newonly=True)
        elif not any((uri.startswith(s) for s in ["http", "file", "/"])):
            LOG.info(f"OCP WARNING: plugins returned no metadata for uri {uri}")

    # events from gui_player/audio_service
    def handle_external_play(self, message):
        """
        Handle 'ovos.common_play.play' Messages. Update the metadata with new
        data received unconditionally, otherwise previous song keys might
        bleed into the new track
        @param message: Message associated with request
        """
        if message.data.get("tracks"):
            # backwards compat / old style
            playlist = message.data["tracks"]
            media = playlist[0]
        else:
            media = message.data.get("media", {})
        if media:
            self.update(media, newonly=False)

    def handle_player_metadata_request(self, message):
        """
        Handle 'gui.player.media.service.get.meta' Messages. Emit a response for
        the GUI to handle new metadata.
        @param message: Message associated with request
        """
        self.bus.emit(message.reply("gui.player.media.service.set.meta",
                                    {"title": self.title,
                                     "image": self.image,
                                     "artist": self.artist}))

    def handle_track_state_change(self, message):
        """
        Handle 'ovos.common_play.track.state' Messages. Update status
        @param message: Message with updated `state` data
        @return:
        """
        state = message.data.get("state")
        if state is None:
            raise ValueError(f"Got state update message with no state: "
                             f"{message}")
        if isinstance(state, int):
            state = TrackState(state)
        if not isinstance(state, TrackState):
            raise ValueError(f"Expected int or TrackState, but got: {state}")

        if state == self.status:
            return
        self.status = state
        LOG.info(f"TrackState changed: {repr(state)}")

        if state == TrackState.PLAYING_SKILL:
            # skill is handling playback internally
            pass
        elif state == TrackState.PLAYING_AUDIOSERVICE:
            # audio service is handling playback
            pass
        elif state == TrackState.PLAYING_VIDEO:
            # ovos common play is handling playback in GUI
            pass
        elif state == TrackState.PLAYING_AUDIO:
            # ovos common play is handling playback in GUI
            pass

        elif state == TrackState.DISAMBIGUATION:
            # alternative results # TODO its this 1 track or a list ?
            pass
        elif state in [TrackState.QUEUED_SKILL,
                       TrackState.QUEUED_VIDEO,
                       TrackState.QUEUED_AUDIOSERVICE]:
            # audio service is handling playback and this is in playlist
            pass

    def handle_media_state_change(self, message):
        """
        Handle 'ovos.common_play.media.state' Messages. If ended, reset.
        @param message: Message with updated MediaState
        """
        state = message.data.get("state")
        if state is None:
            raise ValueError(f"Got state update message with no state: "
                             f"{message}")
        if isinstance(state, int):
            state = MediaState(state)
        if not isinstance(state, MediaState):
            raise ValueError(f"Expected int or TrackState, but got: {state}")
        # Don't do anything. Let OCP manage this object's state
        # if state == MediaState.END_OF_MEDIA:
        #     # playback ended, allow next track to change metadata again
        #     self.reset()

    def handle_sync_seekbar(self, message):
        """
        Handle 'ovos.common_play.playback_time' Messages sent by audio backend
        @param message: Message with 'length' and 'position' data
        """
        self.length = message.data["length"]
        self.position = message.data["position"]

    def handle_sync_trackinfo(self, message):
        """
        Handle 'mycroft.audio.service.track_info_reply' Messages with current
        media defined in message.data
        @param message: Message with dict MediaEntry data
        """
        self.update(message.data)

    def handle_audio_service_play(self, message):
        """
        Handle 'mycroft.audio.service.play' Messages with list of tracks in data
        @param message: Message with 'tracks' data
        """
        tracks = message.data.get("tracks") or []
        # only present in ovos-core
        skill_id = message.context.get("skill_id") or 'mycroft.audio_interface'
        for idx, track in enumerate(tracks):
            # TODO try to extract metadata from uri (latency ?)
            if idx == 0:
                self.update(
                    {"uri": track,
                     "title": track.split("/")[-1],
                     "status": TrackState.QUEUED_AUDIOSERVICE,
                     'skill_id': skill_id,
                     "playback": PlaybackType.AUDIO_SERVICE}
                )
            else:
                # TODO sync playlist ?
                pass

    def handle_audio_service_play_start(self, message):
        """
        Handle 'mycroft.audio.playing_track' Messages
        @param message: Message notifying playback has started
        """
        self.update(
            {"status": TrackState.PLAYING_AUDIOSERVICE,
             "playback": PlaybackType.AUDIO_SERVICE})
