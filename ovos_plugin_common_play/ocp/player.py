import random
from os.path import join, dirname
from time import sleep
from typing import List, Union, Optional

from ovos_bus_client.message import Message
from ovos_config import Configuration
from ovos_utils.gui import is_gui_connected, is_gui_running
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message
from ovos_workshop import OVOSAbstractApplication
from ovos_workshop.backwards_compat import (PluginStream, LoopState, MediaState, PlayerState, TrackState,
                                            PlaybackType, MediaEntry, PlaybackMode, Playlist)

from ovos_plugin_common_play.ocp.constants import OCP_ID
from ovos_plugin_common_play.ocp.gui import OCPMediaPlayerGUI
from ovos_plugin_common_play.ocp.media import NowPlaying
from ovos_plugin_common_play.ocp.mpris import MprisPlayerCtl
from ovos_plugin_common_play.ocp.mycroft_cps import MycroftAudioService
from ovos_plugin_common_play.ocp.search import OCPSearch
from ovos_plugin_common_play.ocp.utils import require_native_source
try:
    from ovos_utils.ocp import dict2entry
except ImportError:  # older utils version
    dict2entry = MediaEntry.from_dict


class OCPMediaPlayer(OVOSAbstractApplication):
    def __init__(self, bus=None, settings=None, lang=None, gui=None,
                 resources_dir=None, skill_id=OCP_ID, validate_source=True,
                 native_sources: Optional[List[str]] = None,
                 **kwargs):
        resources_dir = resources_dir or join(dirname(__file__), "res")
        gui = gui or OCPMediaPlayerGUI(bus=bus)

        self.validate_source = validate_source
        self.native_sources = native_sources or Configuration()["Audio"].\
            get("native_sources", ["debug_cli", "audio"])
        # Define things referenced in `bind`
        self.now_playing: NowPlaying = NowPlaying()
        self.media: OCPSearch = OCPSearch()
        self.state: PlayerState = PlayerState.STOPPED
        self.loop_state: LoopState = LoopState.NONE
        self.media_state: MediaState = MediaState.NO_MEDIA
        self.playlist: Playlist = Playlist()
        self.shuffle: bool = False
        self.audio_service = None
        self._audio_backend = None
        self.track_history = {}  # Dict of track URI to play count

        super().__init__(skill_id=skill_id, bus=bus, gui=gui,
                         resources_dir=resources_dir, lang=lang, **kwargs)
        if settings:
            self.settings.merge(settings)

        self._paused_on_duck = False

        # mpris settings
        manage_players = self.settings.get("manage_external_players", False)
        if self.settings.get('disable_mpris'):
            LOG.info("MPRIS integration is disabled")
            self.mpris = None
        else:
            self.mpris = MprisPlayerCtl(manage_players=manage_players)
            self.mpris.bind(self)

    def bind(self, bus=None):
        """
        Initialize components that need a MessageBusClient or instance of this
        object.
        @param bus: MessageBusClient object to register events on
        """
        super(OCPMediaPlayer, self).bind(bus)
        self.now_playing.bind(self)
        self.media.bind(self)
        self.gui.bind(self)
        self.audio_service = MycroftAudioService(self.bus)
        self.register_bus_handlers()

    def register_bus_handlers(self):
        # audio ducking TODO improve to wait for end of speech ?
        self.add_event('recognizer_loop:record_begin',
                       self.handle_duck_request)
        self.add_event('recognizer_loop:record_end',
                       self.handle_unduck_request)

        # mycroft-gui media service
        self.add_event('gui.player.media.service.sync.status',
                       self.handle_player_state_update)
        self.add_event("gui.player.media.service.get.next",
                       self.handle_next_request)
        self.add_event("gui.player.media.service.get.previous",
                       self.handle_prev_request)
        self.add_event("gui.player.media.service.get.repeat",
                       self.handle_repeat_toggle_request)
        self.add_event("gui.player.media.service.get.shuffle",
                       self.handle_shuffle_toggle_request)

        # ovos common play bus api
        self.add_event('ovos.common_play.player.state',
                       self.handle_player_state_update)
        self.add_event('ovos.common_play.media.state',
                       self.handle_player_media_update)
        self.add_event('ovos.common_play.play',
                       self.handle_play_request)
        self.add_event('ovos.common_play.pause',
                       self.handle_pause_request)
        self.add_event('ovos.common_play.resume',
                       self.handle_resume_request)
        self.add_event('ovos.common_play.stop',
                       self.handle_stop_request)
        self.add_event('ovos.common_play.next',
                       self.handle_next_request)
        self.add_event('ovos.common_play.previous',
                       self.handle_prev_request)
        self.add_event('ovos.common_play.seek',
                       self.handle_seek_request)
        self.add_event('ovos.common_play.get_track_length',
                       self.handle_track_length_request)
        self.add_event('ovos.common_play.set_track_position',
                       self.handle_set_track_position_request)
        self.add_event('ovos.common_play.get_track_position',
                       self.handle_track_position_request)
        self.add_event('ovos.common_play.track_info',
                       self.handle_track_info_request)
        self.add_event('ovos.common_play.list_backends',
                       self.handle_list_backends_request)
        self.add_event('ovos.common_play.playlist.set',
                       self.handle_playlist_set_request)
        self.add_event('ovos.common_play.playlist.clear',
                       self.handle_playlist_clear_request)
        self.add_event('ovos.common_play.playlist.queue',
                       self.handle_playlist_queue_request)
        self.add_event('ovos.common_play.duck',
                       self.handle_duck_request)
        self.add_event('ovos.common_play.unduck',
                       self.handle_unduck_request)
        self.add_event('ovos.common_play.shuffle.set',
                       self.handle_set_shuffle)
        self.add_event('ovos.common_play.shuffle.unset',
                       self.handle_unset_shuffle)
        self.add_event('ovos.common_play.repeat.set',
                       self.handle_set_repeat)
        self.add_event('ovos.common_play.repeat.unset',
                       self.handle_unset_repeat)

        # GUI Configuration Events
        self.add_event('ovos.common_play.gui.enable_app_timeout',
                       self.handle_enable_app_timeout)
        self.add_event('ovos.common_play.gui.set_app_timeout',
                       self.handle_set_app_timeout)
        self.add_event('ovos.common_play.gui.timeout.mode',
                       self.handle_set_app_timeout_mode)

    @property
    def active_skill(self) -> str:
        """
        Return the skill_id of the skill providing the current media
        """
        return self.now_playing.skill_id

    @property
    def active_backend(self) -> PlaybackType:
        """
        Return the PlaybackType for the current media
        """
        return self.now_playing.playback

    @property
    def tracks(self) -> List[MediaEntry]:
        """
        Return the current queue as a list of MediaEntry objects
        """
        return self.playlist.entries

    @property
    def disambiguation(self) -> List[MediaEntry]:
        """
        Return a list of the previous search results as MediaEntry objects
        """
        return self.media.search_playlist.entries

    @property
    def can_prev(self) -> bool:
        """
        Return true if there is a previous track in the queue to skip to
        """
        if self.active_backend != PlaybackType.MPRIS and \
                self.playlist.is_first_track:
            return False
        return True

    @property
    def can_next(self) -> bool:
        """
        Return true if there is a next track in the queue to skip to
        """
        if self.loop_state != LoopState.NONE or \
                self.shuffle or \
                self.active_backend == PlaybackType.MPRIS:
            return True
        elif self.settings.get("merge_search", True) and \
                not self.media.search_playlist.is_last_track:
            return True
        elif not self.playlist.is_last_track:
            return True
        return False

    # state
    def set_media_state(self, state: MediaState):
        """
        Set self.media_state and emit an event announcing this state change.
        @param state: New MediaState
        """
        if not isinstance(state, MediaState):
            raise TypeError(f"Expected MediaState and got: {state}")
        if state == self.media_state:
            return
        self.media_state = state
        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": self.media_state}))

    def set_player_state(self, state: PlayerState):
        """
        Set self.state, update the GUI and MPRIS (if available), and emit an
        event announcing this state change.
        @param state: New PlayerState
        """
        if not isinstance(state, PlayerState):
            raise TypeError(f"Expected PlayerState and got: {state}")
        if state == self.state:
            return
        self.state = state
        state2str = {PlayerState.PLAYING: "Playing",
                     PlayerState.PAUSED: "Paused",
                     PlayerState.STOPPED: "Stopped"}
        self.gui["status"] = state2str[self.state]
        if self.mpris:
            self.mpris.update_props({"CanPause": self.state == PlayerState.PLAYING,
                                     "CanPlay": self.state == PlayerState.PAUSED,
                                     "PlaybackStatus": state2str[state]})
        self.bus.emit(Message("ovos.common_play.player.state",
                              {"state": self.state}))

    def set_now_playing(self, track: Union[dict, MediaEntry, Playlist, PluginStream]):
        """
        Set `track` as the currently playing media, update the playlist, and
        notify any GUI or MPRIS clients. Adds `track` to `playlist`
        @param track: MediaEntry or dict representation of a MediaEntry to play
        """
        LOG.debug(f"Playing: {track}")
        if isinstance(track, dict):
            LOG.debug(f"Handling dict track: {track}")
            if "uri" not in track:  # TODO handle this better
                track["uri"] = "external:"  # when syncing from MPRIS uri is missing
            track = dict2entry(track)
        if not isinstance(track, (MediaEntry, Playlist, PluginStream)):
            raise ValueError(f"Expected MediaEntry/Playlist, but got: {track}")

        try:
            idx = self.playlist.index(track)  # find the entry in "now playing"
        except ValueError:
            idx = -1
        if isinstance(track, PluginStream):
            track = track.extract_media_entry(video=track.playback == PlaybackType.VIDEO)
            LOG.info(f"PluginStream extracted: {track}")
            if idx >= 0:
                self.playlist[idx] = track  # update extracted plugin stream

        if isinstance(track, MediaEntry):
            # single track entry (MediaEntry)
            self.now_playing.update(track)

            # update playlist position
            if idx > -1:
                self.playlist.set_position(idx)
            # add to "now playing" if it's a new track
            elif track not in self.playlist:  # compared by uri
                self.playlist.add_entry(track)
                self.playlist.set_position(len(self.playlist) - 1)
            # find equivalent track position in playlist
            else:
                self.playlist.goto_track(track)

        elif isinstance(track, Playlist):
            # this is a playlist result (list of dicts)
            self.playlist.clear()
            for entry in track:
                self.playlist.add_entry(entry)

            # mew playlist -> reset playlist position to the start
            self.playlist.set_position(0)

            # update self.now_playing
            if len(self.playlist):
                track = self.playlist[0]
                return self.set_now_playing(track)

            # If there's no URI, the skill might be handling playback so
            # now_playing should still be updated
            self.now_playing.update(self.playlist.as_dict)

        # update gui values
        self.gui.update_current_track()
        self.gui.update_playlist()
        if self.mpris:
            self.mpris.update_props(
                {"Metadata": self.now_playing.mpris_metadata}
            )

    # stream handling
    def validate_stream(self) -> bool:
        """
        Validate that self.now_playing is playable and update the GUI if it is
        @return: True if the `now_playing` stream can be handled
        """
        if self.now_playing.is_cps:
            self.now_playing.playback = PlaybackType.SKILL

        if self.active_backend not in [PlaybackType.SKILL,
                                       PlaybackType.UNDEFINED,
                                       PlaybackType.MPRIS]:
            has_gui = is_gui_running() or is_gui_connected(self.bus)
            if not has_gui or self.settings.get("force_audioservice", False) or \
                    self.settings.get("playback_mode") == PlaybackMode.FORCE_AUDIOSERVICE:
                # No gui, so lets force playback to use audio only
                LOG.debug("Casting to PlaybackType.AUDIO_SERVICE")
                self.now_playing.playback = PlaybackType.AUDIO_SERVICE
            if not self.now_playing.uri:
                return False
        self.now_playing.extract_stream()
        self.gui["stream"] = self.now_playing.uri
        self.gui.update_current_track()
        return True

    def on_invalid_media(self):
        """
        Handle media playback errors. Show an error and play the next track.
        """
        LOG.warning(f"Failed to play: {self.now_playing}")
        self.gui.show_playback_error()
        self.play_next()

    # media controls
    def play_media(self, track: Union[dict, MediaEntry, PluginStream, Playlist],
                   disambiguation: List[Union[dict, MediaEntry]] = None,
                   playlist: List[Union[dict, MediaEntry]] = None):
        """
        Start playing the requested media, replacing any current playback.
        @param track: dict or MediaEntry to start playing
        @param disambiguation: list of tracks returned from search
        @param playlist: list of tracks in the current playlist
        """
        if isinstance(track, dict):
            track = dict2entry(track)
        if not isinstance(track, (MediaEntry, Playlist, PluginStream)):
            raise TypeError(f"Expected MediaEntry/Playlist, got: {track}")
        if isinstance(track, Playlist) and not playlist:
            playlist = track
            track = playlist[0]
        if self.mpris:
            self.mpris.stop()
        if self.state == PlayerState.PLAYING:
            self.pause()  # make it more responsive
        if disambiguation:
            self.media.search_playlist.replace(disambiguation)
            self.media.search_playlist.sort_by_conf()
            self.gui.update_search_results()
        if playlist:
            self.playlist.replace(playlist)
        if track in self.playlist:
            self.playlist.goto_track(track)
        self.set_now_playing(track)
        self.play()

    @property
    def audio_service_player(self) -> str:
        """
        Return the configured audio player that is handling playback
        """
        if not self._audio_backend:
            self._audio_backend = self._get_preferred_audio_backend()
        return self._audio_backend

    def _get_preferred_audio_backend(self):
        """
        Check configuration and available backends to select a preferred backend

        NOTE - the bus api tells us what backends are loaded,however it does not
        provide "type", so we need to get that from config we still hit the
        messagebus to account for loading failures, even if config claims
        backend is enabled it might not load
        """
        cfg = Configuration()["Audio"]["backends"]
        available = [k for k, v in cfg.items()
                     if v.get("type", "") != "ovos_common_play"]
        preferred = self.settings.get("preferred_audio_services") or \
                    ["vlc", "simple"]
        for b in preferred:
            if b in available:
                return b
        LOG.error("Preferred audio service backend not installed")
        return "simple"

    def play(self):
        """
        Start playback of the current `now_playing` MediaEntry. Displays the GUI
        player, updates track history, emits events for any listeners, and
        updates mpris (if configured).
        """
        # stop any external media players
        if self.mpris and not self.mpris.stop_event.is_set():
            LOG.info("Requested playback with mpris not stopped")
            self.mpris.stop()
        # validate new stream
        # TODO buffering animation ?
        if not self.validate_stream():
            LOG.warning("Stream Validation Failed")
            self.on_invalid_media()
            return
        self.gui.show_player()

        self.track_history.setdefault(self.now_playing.uri, 0)
        self.track_history[self.now_playing.uri] += 1

        LOG.debug(f"Requesting playback: {repr(self.active_backend)}")
        if self.active_backend == PlaybackType.AUDIO and not is_gui_running():
            # NOTE: this is already normalized in self.validate_stream, using messagebus
            # if we get here the GUI probably crashed, or just isnt "mycroft-gui-app" or "ovos-shell"
            # is_gui_running() can not be trusted, log a warning only
            LOG.warning("Requested Audio playback via GUI, but GUI doesn't seem to be running?")

        if self.active_backend == PlaybackType.AUDIO_SERVICE:
            LOG.debug("Handling playback via audio_service")
            # we explicitly want to use an audio backend for audio only output
            self.audio_service.play(self.now_playing.uri,
                                    utterance=self.audio_service_player)
            self.bus.emit(Message("ovos.common_play.track.state", {
                "state": TrackState.PLAYING_AUDIOSERVICE}))
            self.set_player_state(PlayerState.PLAYING)
        elif self.active_backend == PlaybackType.AUDIO:
            LOG.debug("Handling playback via gui")
            # handle audio natively in mycroft-gui
            sleep(2)  # wait for gui page to start or this is sent before page
            self.bus.emit(Message("gui.player.media.service.play", {
                "track": self.now_playing.uri,
                "mime": self.now_playing.mimetype,
                "repeat": False}))
            sleep(0.2)  # wait for the above message to be processed
            self.bus.emit(Message("ovos.common_play.track.state", {
                "state": TrackState.PLAYING_AUDIO}))
        elif self.active_backend == PlaybackType.SKILL:
            LOG.debug("Requesting playback: PlaybackType.SKILL")
            if self.now_playing.is_cps:  # mycroft-core compat layer
                LOG.debug("     - Mycroft common play result selected")
                self.bus.emit(Message('play:start',
                                      {"skill_id": self.now_playing.skill_id,
                                       "callback_data": self.now_playing.cps_data,
                                       "phrase": self.now_playing.phrase}))
            else:
                self.bus.emit(Message(
                    f'ovos.common_play.{self.now_playing.skill_id}.play',
                    self.now_playing.info))
            self.bus.emit(Message("ovos.common_play.track.state", {
                "state": TrackState.PLAYING_SKILL}))
        elif self.active_backend == PlaybackType.VIDEO:
            LOG.debug("Requesting playback: PlaybackType.VIDEO")
            # handle video natively in mycroft-gui
            self.bus.emit(Message("gui.player.media.service.play", {
                "track": self.now_playing.uri,
                "mime": self.now_playing.mimetype,
                "repeat": False}))
            self.bus.emit(Message("ovos.common_play.track.state", {
                "state": TrackState.PLAYING_VIDEO}))
        elif self.active_backend == PlaybackType.WEBVIEW:
            LOG.debug("Requesting playback: PlaybackType.WEBVIEW")
            # open a url in native webview in mycroft-gui
            self.bus.emit(Message("ovos.common_play.track.state", {
                "state": TrackState.PLAYING_WEBVIEW}))
        else:
            raise ValueError("invalid playback request")
        if self.mpris:
            self.mpris.update_props({"CanGoNext": self.can_next})
            self.mpris.update_props({"CanGoPrevious": self.can_prev})
        LOG.debug(f"self.active_backend={repr(self.active_backend)}")

    def play_shuffle(self):
        """
        Go to a random position in the playlist and set that MediaEntry as
        'now_playing` (does NOT call 'play').
        """
        LOG.debug("Shuffle == True")
        if len(self.playlist) > 1 and not self.playlist.is_last_track:
            # TODO: does the 'last track' matter in this case?
            self.playlist.set_position(random.randint(0, len(self.playlist)))
            self.set_now_playing(self.playlist.current_track)
        else:
            self.media.search_playlist.next_track()
            self.set_now_playing(self.media.search_playlist.current_track)

    def play_next(self):
        """
        Play the next track in the playlist or search results.
        End playback if there is no next track, accounting for repeat and
        shuffle settings.
        """
        if self.active_backend == PlaybackType.UNDEFINED:
            LOG.error("self.active_backend is undefined")
        elif self.active_backend in [PlaybackType.MPRIS]:
            if self.mpris:
                self.mpris.play_next()
            return
        elif self.active_backend in [PlaybackType.SKILL]:
            LOG.debug(f"Defer playing next track to skill")
            self.bus.emit(Message(
                f'ovos.common_play.{self.now_playing.skill_id}.next'))
            return
        self.pause()  # make more responsive

        if self.loop_state == LoopState.REPEAT_TRACK:
            LOG.debug("Repeating single track")
        elif self.shuffle:
            LOG.debug("Shuffling")
            self.play_shuffle()
        elif not self.playlist.is_last_track:
            self.playlist.next_track()
            self.set_now_playing(self.playlist.current_track)
            LOG.info(f"Next track index: {self.playlist.position}")
        elif not self.media.search_playlist.is_last_track and \
                self.settings.get("merge_search", True):
            while self.media.search_playlist.current_track in self.playlist:
                # Don't play media already played from the playlist
                self.media.search_playlist.next_track()
            self.set_now_playing(self.media.search_playlist.current_track)
            LOG.info(f"Next search index: "
                     f"{self.media.search_playlist.position}")
        else:
            if self.loop_state == LoopState.REPEAT and len(self.playlist):
                LOG.info("end of playlist, repeat == True")
                self.playlist.set_position(0)
            else:
                LOG.info("requested next, but there aren't any more tracks")
                self.gui.handle_end_of_playback()
                return
        self.play()

    def play_prev(self):
        """
        Play the previous track in the playlist.
        If there is no previous track, do nothing.
        """
        if self.active_backend in [PlaybackType.MPRIS]:
            if self.mpris:
                self.mpris.play_prev()
            return
        elif self.active_backend in [PlaybackType.SKILL,
                                     PlaybackType.UNDEFINED]:
            self.bus.emit(Message(
                f'ovos.common_play.{self.now_playing.skill_id}.prev'))
            return
        self.pause()  # make more responsive

        if self.shuffle:
            # TODO: Should skipping back get a random track instead of previous?
            self.play_shuffle()
        elif not self.playlist.is_first_track:
            self.playlist.prev_track()
            self.set_now_playing(self.playlist.current_track)
            LOG.debug(f"Previous track index: {self.playlist.position}")
            self.play()
        else:
            LOG.debug("requested previous, but already in 1st track")

    def pause(self):
        """
        Ask the current playback to pause.
        """
        LOG.debug(f"Pausing playback: {self.active_backend}")
        if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                   PlaybackType.UNDEFINED]:
            self.audio_service.pause()
        if self.active_backend in [PlaybackType.AUDIO,
                                   PlaybackType.VIDEO,
                                   PlaybackType.UNDEFINED]:
            self.bus.emit(Message("gui.player.media.service.pause"))
        if self.active_backend in [PlaybackType.SKILL,
                                   PlaybackType.UNDEFINED]:
            self.bus.emit(Message(f'ovos.common_play'
                                  f'.{self.active_skill}.pause'))
        if self.active_backend in [PlaybackType.MPRIS] and self.mpris:
            self.mpris.pause()
        self.set_player_state(PlayerState.PAUSED)
        self._paused_on_duck = False

    def resume(self):
        """
        Ask any paused or stopped playback to resume.
        """
        LOG.debug(f"Resuming playback: {self.active_backend}")
        if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                   PlaybackType.UNDEFINED]:
            self.audio_service.resume()

        if self.active_backend in [PlaybackType.SKILL,
                                   PlaybackType.UNDEFINED]:
            self.bus.emit(
                Message(f'ovos.common_play.{self.active_skill}.resume'))

        if self.active_backend in [PlaybackType.AUDIO,
                                   PlaybackType.VIDEO]:
            self.bus.emit(Message('gui.player.media.service.resume'))

        if self.active_backend in [PlaybackType.MPRIS] and self.mpris:
            self.mpris.resume()

        self.set_player_state(PlayerState.PLAYING)

    def seek(self, position: int):
        """
        Request playback to go to a specific position in the current media
        @param position: milliseconds position to seek to
        """
        if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                   PlaybackType.UNDEFINED]:
            self.audio_service.set_track_position(position / 1000)
        self.gui["position"] = position

    def stop(self):
        """
        Request stopping current playback and searching
        """
        # stop any search still happening
        self.bus.emit(Message("ovos.common_play.search.stop"))

        LOG.debug("clearing playlist")
        self.playlist.clear()  # needed to ensure next track doesnt track due to autoplay

        LOG.debug("Stopping playback")
        if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                   PlaybackType.UNDEFINED]:
            self.stop_audio_service()
            self.set_player_state(PlayerState.STOPPED)
        if self.active_backend in [PlaybackType.SKILL,
                                   PlaybackType.UNDEFINED]:
            self.stop_audio_skill()
        if self.active_backend in [PlaybackType.AUDIO,
                                   PlaybackType.VIDEO,
                                   PlaybackType.UNDEFINED]:
            self.stop_gui_player()
            self.set_player_state(PlayerState.STOPPED)
        # if self.active_backend in [PlaybackType.MPRIS] and self.mpris:
        #    self.mpris.stop()

    def stop_gui_player(self):
        """
        Emit a Message notifying the gui player to stop
        """
        self.bus.emit(Message("gui.player.media.service.stop"))

    def stop_audio_skill(self):
        """
        Emit a Message notifying self.active_skill to stop
        """
        self.bus.emit(Message(f'ovos.common_play.{self.active_skill}.stop'))

    def stop_audio_service(self):
        """
        Call self.audio_service.stop()
        """
        self.audio_service.stop()

    def reset(self):
        """
        Reset this instance to clear any media or settings
        """
        self.stop()
        self.playlist.clear()
        self.media.clear()
        self.set_media_state(MediaState.NO_MEDIA)
        self.shuffle = False
        self.loop_state = LoopState.NONE

    def shutdown(self):
        """
        Shutdown this instance and its spawned objects. Remove events.
        """
        self.stop()
        if self.mpris:
            self.mpris.shutdown()
        self.now_playing.shutdown()
        self.gui.shutdown()
        self.media.shutdown()
        self.remove_event('recognizer_loop:record_begin')
        self.remove_event('recognizer_loop:record_end')
        self.remove_event('gui.player.media.service.sync.status')
        self.remove_event("gui.player.media.service.get.next")
        self.remove_event("gui.player.media.service.get.previous")

    # player -> common play
    @require_native_source()
    def handle_player_state_update(self, message):
        """
        Handles 'gui.player.media.service.sync.status' and
        'ovos.common_play.player.state' messages with player state updates
        @param message: Message providing new "state" data
        """
        state = message.data.get("state")
        if state is None:
            raise ValueError(f"Got state update message with no state: "
                             f"{message}")
        if isinstance(state, int):
            state = PlayerState(state)
        if not isinstance(state, PlayerState):
            raise ValueError(f"Expected int or PlayerState, but got: {state}")
        if state == self.state:
            return
        LOG.info(f"PlayerState changed: {repr(state)}")
        if state == PlayerState.PLAYING:
            self.state = PlayerState.PLAYING
        elif state == PlayerState.PAUSED:
            self.state = PlayerState.PAUSED
            if self.app_view_timeout_enabled and \
                    self.app_view_timeout_mode == "pause":
                LOG.debug("Starting GUI pause timeout counter")
                self.gui.cancel_app_view_timeout()
                self.gui.schedule_app_view_pause_timeout()
        elif state == PlayerState.STOPPED:
            self.state = PlayerState.STOPPED

        if self.mpris:
            state2str = {PlayerState.PLAYING: "Playing",
                         PlayerState.PAUSED: "Paused",
                         PlayerState.STOPPED: "Stopped"}
            self.mpris.update_props({"CanPause": state == PlayerState.PLAYING,
                                     "CanPlay": state == PlayerState.PAUSED,
                                     "PlaybackStatus": state2str[state]})

    @require_native_source()
    def handle_player_media_update(self, message):
        """
        Handles 'ovos.common_play.media.state' messages with media state updates
        @param message: Message providing new "state" data
        """
        LOG.debug(f"backend={repr(self.active_backend)}|"
                  f"msg_type={message.msg_type}")
        state = message.data.get("state")
        if state is None:
            raise ValueError(f"Got state update message with no state: "
                             f"{message}")
        if isinstance(state, int):
            state = MediaState(state)
        if not isinstance(state, MediaState):
            raise ValueError(f"Expected int or MediaState, but got: {state}")
        if state == self.media_state:
            return
        LOG.debug(f"MediaState changed: {repr(state)}")
        self.media_state = state
        if state == MediaState.END_OF_MEDIA:
            self.handle_playback_ended(message)
        elif state == MediaState.INVALID_MEDIA:
            self.handle_invalid_media(message)
            if self.settings.get("autoplay", True):
                self.play_next()

    @require_native_source()
    def handle_invalid_media(self, message):
        self.gui.show_playback_error()

    @require_native_source()
    def handle_playback_ended(self, message):
        # TODO: When we get here, self.active_backend has been reset!
        LOG.info(f"END OF MEDIA - playlist pos: {self.playlist.position} "
                  f"total tracks: {len(self.playlist)} "
                 f"backend: {self.active_backend}")
        go_next = self.settings.get("autoplay", True) and \
                self.active_backend != PlaybackType.MPRIS and \
                self.playlist.position + 1 < len(self.playlist)
        LOG.debug(f"Go to Next track: {go_next}")
        if go_next:
            self.play_next()
            return
        LOG.info("Playback ended")
        self.gui.handle_end_of_playback(message)

    # ovos common play bus api requests
    @require_native_source()
    def handle_play_request(self, message):
        LOG.debug("Received external OVOS playback request")
        repeat = message.data.get("repeat", False)
        if repeat:
            self.loop_state = LoopState.REPEAT

        if message.data.get("tracks"):
            # backwards compat / old style
            playlist = disambiguation = message.data["tracks"]
            media = playlist[0]
        else:
            media = message.data.get("media")
            playlist = message.data.get("playlist") or [media]
            disambiguation = message.data.get("disambiguation") or [media]
        self.play_media(media, disambiguation, playlist)

    @require_native_source()
    def handle_pause_request(self, message):
        self.pause()

    @require_native_source()
    def handle_stop_request(self, message):
        self.stop()

    @require_native_source()
    def handle_resume_request(self, message):
        self.resume()

    @require_native_source()
    def handle_seek_request(self, message):
        # from bus api
        miliseconds = message.data.get("seconds", 0) * 1000

        # from audio player GUI
        position = message.data.get("seekValue")
        if not position:
            position = self.now_playing.position or 0
            if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                       PlaybackType.UNDEFINED]:
                position = self.audio_service.get_track_position() or position
            position += miliseconds
        self.seek(position)

    @require_native_source()
    def handle_next_request(self, message):
        self.play_next()

    @require_native_source()
    def handle_prev_request(self, message):
        self.play_prev()

    @require_native_source()
    def handle_set_shuffle(self, message):
        self.shuffle = True
        self.gui.update_seekbar_capabilities()

    @require_native_source()
    def handle_unset_shuffle(self, message):
        self.shuffle = False
        self.gui.update_seekbar_capabilities()

    @require_native_source()
    def handle_set_repeat(self, message):
        self.loop_state = LoopState.REPEAT
        self.gui.update_seekbar_capabilities()

    @require_native_source()
    def handle_unset_repeat(self, message):
        self.loop_state = LoopState.NONE
        self.gui.update_seekbar_capabilities()

    # playlist control bus api
    @require_native_source()
    def handle_repeat_toggle_request(self, message):
        if self.loop_state == LoopState.REPEAT_TRACK:
            self.loop_state = LoopState.NONE
        elif self.loop_state == LoopState.REPEAT:
            self.loop_state = LoopState.REPEAT_TRACK
        elif self.loop_state == LoopState.NONE:
            self.loop_state = LoopState.REPEAT
        LOG.info(f"Repeat: {self.loop_state}")
        self.gui.update_seekbar_capabilities()

    @require_native_source()
    def handle_shuffle_toggle_request(self, message):
        self.shuffle = not self.shuffle
        LOG.info(f"Shuffle: {self.shuffle}")
        self.gui.update_seekbar_capabilities()

    @require_native_source()
    def handle_playlist_set_request(self, message):
        self.playlist.clear()
        self.handle_playlist_queue_request(message)

    @require_native_source()
    def handle_playlist_queue_request(self, message):
        for track in message.data["tracks"]:
            self.playlist.add_entry(track)
        self.gui.update_playlist()

    @require_native_source()
    def handle_playlist_clear_request(self, message):
        self.playlist.clear()
        self.set_media_state(MediaState.NO_MEDIA)
        self.gui.update_playlist()

    # audio ducking
    @require_native_source()
    def handle_duck_request(self, message):
        """
        Pause audio on 'recognizer_loop:record_begin'
        @param message: Message associated with event
        """
        if self.state == PlayerState.PLAYING:
            self.pause()
            self._paused_on_duck = True

    @require_native_source()
    def handle_unduck_request(self, message):
        """
        Resume paused audio on 'recognizer_loop:record_begin'
        @param message: Message associated with event
        """
        if self.state == PlayerState.PAUSED and self._paused_on_duck:
            self.resume()
            self._paused_on_duck = False

    # track data
    @require_native_source()
    def handle_track_length_request(self, message):
        l = self.now_playing.length
        if self.active_backend == PlaybackType.AUDIO_SERVICE:
            l = self.audio_service.get_track_length() or l
        data = {"length": l}
        self.bus.emit(message.response(data))

    @require_native_source()
    def handle_track_position_request(self, message):
        pos = self.now_playing.position
        if self.active_backend == PlaybackType.AUDIO_SERVICE:
            pos = self.audio_service.get_track_position() or pos
        data = {"position": pos}
        self.bus.emit(message.response(data))

    @require_native_source()
    def handle_set_track_position_request(self, message):
        miliseconds = message.data.get("position")
        self.seek(miliseconds)

    @require_native_source()
    def handle_track_info_request(self, message):
        data = self.now_playing.as_dict
        if self.active_backend == PlaybackType.AUDIO_SERVICE:
            data = self.audio_service.track_info() or data
        self.bus.emit(message.response(data))

    # internal info
    @require_native_source()
    def handle_list_backends_request(self, message):
        data = self.audio_service.available_backends()
        self.bus.emit(message.response(data))

    # app timeout
    @property
    def app_view_timeout_enabled(self):
        return self.settings.get("app_view_timeout_enabled", False)

    @property
    def app_view_timeout_value(self):
        return self.settings.get("app_view_timeout", 30)

    @property
    def app_view_timeout_mode(self):
        return self.settings.get("app_view_timeout_mode", "all")

    @require_native_source()
    def handle_enable_app_timeout(self, message):
        self.settings["app_view_timeout_enabled"] = message.data.get("enabled", False)
        self.settings.store()
        if not self.app_view_timeout_enabled:
            self.gui.cancel_app_view_timeout()

    @require_native_source()
    def handle_set_app_timeout(self, message):
        # timeout in seconds: 15 | 30 | 45 | 60
        self.settings["app_view_timeout"] = message.data.get("timeout", 30)
        self.settings.store()
        self.gui.cancel_app_view_timeout(restart=True)

    @require_native_source()
    def handle_set_app_timeout_mode(self, message):
        # timeout modes: all | pause
        self.settings["app_view_timeout_mode"] = message.data.get("mode", "all")
        self.settings.store()
        self.gui["app_view_timeout_mode"] = self.settings.get("app_view_timeout_mode", "all")
        self.gui.cancel_app_view_timeout()
