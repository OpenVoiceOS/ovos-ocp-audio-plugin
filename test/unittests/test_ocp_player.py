import json
import unittest

from mycroft_bus_client import Message
from ovos_utils.messagebus import FakeBus
from unittest.mock import Mock, patch

from ovos_plugin_common_play.ocp.player import OCPMediaPlayer
from ovos_plugin_common_play.ocp.media import MediaEntry
from ovos_plugin_common_play.ocp.status import MediaType, LoopState, \
    MediaState, PlaybackType, TrackState, PlayerState


valid_search_results = [
    {'media_type': MediaType.MUSIC,
     'playback': PlaybackType.AUDIO,
     'image': 'https://freemusicarchive.org/legacy/fma-smaller.jpg',
     'skill_icon': 'https://freemusicarchive.org/legacy/fma-smaller.jpg',
     'uri': 'https://freemusicarchive.org/track/07_-_Quantum_Jazz_-_Orbiting_A_Distant_Planet/stream/',
     'title': 'Orbiting A Distant Planet',
     'artist': 'Quantum Jazz',
     'match_confidence': 65},
    {'media_type': MediaType.MUSIC,
     'playback': PlaybackType.AUDIO,
     'image': 'https://freemusicarchive.org/legacy/fma-smaller.jpg',
     'skill_icon': 'https://freemusicarchive.org/legacy/fma-smaller.jpg',
     'uri': 'https://freemusicarchive.org/track/05_-_Quantum_Jazz_-_Passing_Fields/stream/',
     'title': 'Passing Fields',
     'artist': 'Quantum Jazz',
     'match_confidence': 65},
    {'media_type': MediaType.MUSIC,
     'playback': PlaybackType.AUDIO,
     'image': 'https://freemusicarchive.org/legacy/fma-smaller.jpg',
     'skill_icon': 'https://freemusicarchive.org/legacy/fma-smaller.jpg',
     'uri': 'https://freemusicarchive.org/track/04_-_Quantum_Jazz_-_All_About_The_Sun/stream/',
     'title': 'All About The Sun',
     'artist': 'Quantum Jazz',
     'match_confidence': 65}
]


class TestOCPPlayer(unittest.TestCase):
    bus = FakeBus()
    player = OCPMediaPlayer(bus)
    emitted_msgs = []

    @classmethod
    def setUpClass(cls) -> None:
        def get_msg(msg):
            msg = Message.deserialize(msg)
            cls.emitted_msgs.append(msg)

        cls.bus.on("message", get_msg)

    def test_00_player_init(self):
        from ovos_plugin_common_play.ocp.gui import OCPMediaPlayerGUI
        from ovos_plugin_common_play.ocp.search import OCPSearch
        from ovos_plugin_common_play.ocp.media import NowPlaying, Playlist
        from ovos_plugin_common_play.ocp.mpris import MprisPlayerCtl
        from ovos_utils.skills.audioservice import ClassicAudioServiceInterface
        from ovos_workshop import OVOSAbstractApplication

        self.assertIsInstance(self.player, OVOSAbstractApplication)
        self.assertIsInstance(self.player.gui, OCPMediaPlayerGUI)
        self.assertIsInstance(self.player.now_playing, NowPlaying)
        self.assertIsInstance(self.player.media, OCPSearch)
        self.assertIsInstance(self.player.playlist, Playlist)
        self.assertIsInstance(self.player.settings, dict)
        self.assertIsInstance(self.player.mpris, MprisPlayerCtl)

        self.assertEqual(self.player.state, PlayerState.STOPPED)
        self.assertEqual(self.player.loop_state, LoopState.NONE)
        self.assertEqual(self.player.media_state, MediaState.NO_MEDIA)
        self.assertEqual(self.player.track_history, dict())
        self.assertFalse(self.player.shuffle)
        # self.assertIsNone(self.player.audio_service)

        # Testing `bind` method
        self.assertEqual(self.player.now_playing._player, self.player)
        self.assertEqual(self.player.media._player, self.player)
        self.assertEqual(self.player.gui.player, self.player)
        self.assertIsInstance(self.player.audio_service, ClassicAudioServiceInterface)

        bus_events = ['recognizer_loop:record_begin',
                      'recognizer_loop:record_end',
                      'gui.player.media.service.sync.status',
                      "gui.player.media.service.get.next",
                      "gui.player.media.service.get.previous",
                      "gui.player.media.service.get.repeat",
                      "gui.player.media.service.get.shuffle",
                      'ovos.common_play.player.state',
                      'ovos.common_play.media.state',
                      'ovos.common_play.play',
                      'ovos.common_play.pause',
                      'ovos.common_play.resume',
                      'ovos.common_play.stop',
                      'ovos.common_play.next',
                      'ovos.common_play.previous',
                      'ovos.common_play.seek',
                      'ovos.common_play.get_track_length',
                      'ovos.common_play.set_track_position',
                      'ovos.common_play.get_track_position',
                      'ovos.common_play.track_info',
                      'ovos.common_play.list_backends',
                      'ovos.common_play.playlist.set',
                      'ovos.common_play.playlist.clear',
                      'ovos.common_play.playlist.queue',
                      'ovos.common_play.duck',
                      'ovos.common_play.unduck',
                      'ovos.common_play.shuffle.set',
                      'ovos.common_play.shuffle.unset',
                      'ovos.common_play.repeat.set',
                      'ovos.common_play.repeat.unset',
                      'ovos.common_play.gui.enable_app_timeout',
                      'ovos.common_play.gui.set_app_timeout',
                      'ovos.common_play.gui.timeout.mode'
                      ]
        now_playing_events = ["ovos.common_play.track.state",
                              "ovos.common_play.media.state",
                              "ovos.common_play.play",
                              "ovos.common_play.playback_time",
                              'gui.player.media.service.get.meta',
                              'mycroft.audio.service.track_info_reply',
                              'mycroft.audio.service.play',
                              'mycroft.audio.playing_track'
                              ]
        for event in bus_events:
            expected_listeners = 1
            if event in now_playing_events:
                expected_listeners += 1
            self.assertEqual(len(self.bus.ee.listeners(event)),
                             expected_listeners, event)

        # Test properties
        self.assertEqual(self.player.active_skill, "ovos.common_play")
        self.assertEqual(self.player.active_backend, PlaybackType.UNDEFINED)
        self.assertEqual(self.player.tracks, list())
        self.assertEqual(self.player.disambiguation, list())
        self.assertFalse(self.player.can_prev)
        self.assertFalse(self.player.can_next)
        self.assertIsInstance(self.player.audio_service_player, str)
        self.assertIsInstance(self.player.app_view_timeout_enabled, bool)
        self.assertIsInstance(self.player.app_view_timeout_value, int)
        self.assertIsInstance(self.player.app_view_timeout_mode, str)

    def test_set_media_state(self):
        self.player.set_media_state(MediaState.UNKNOWN)

        # Emitted update on state change
        self.player.set_media_state(MediaState.NO_MEDIA)
        last_message = self.emitted_msgs[-1]
        self.assertEqual(last_message.msg_type, "ovos.common_play.media.state")
        self.assertEqual(last_message.data, {"state": MediaState.NO_MEDIA})
        self.assertEqual(self.player.media_state, MediaState.NO_MEDIA)

        # No emit on same state
        self.player.set_media_state(MediaState.NO_MEDIA)
        self.assertEqual(last_message, self.emitted_msgs[-1])
        self.assertEqual(self.player.media_state, MediaState.NO_MEDIA)

        # Test invalid state change
        with self.assertRaises(TypeError):
            self.player.set_media_state(1)
        self.assertEqual(self.player.media_state, MediaState.NO_MEDIA)

    def test_set_player_state(self):
        real_update_props = self.player.mpris.update_props
        self.player.mpris.update_props = Mock()
        self.player.set_player_state(PlayerState.STOPPED)

        # Change to "Playing"
        self.player.set_player_state(PlayerState.PLAYING)
        self.assertEqual(self.player.state, PlayerState.PLAYING)
        self.assertEqual(self.player.gui["status"], "Playing")
        self.player.mpris.update_props.assert_called_with(
            {"CanPause": True, "CanPlay": False, "PlaybackStatus": "Playing"})
        last_message = self.emitted_msgs[-1]
        self.assertEqual(last_message.msg_type, "ovos.common_play.player.state")
        self.assertEqual(last_message.data, {"state": PlayerState.PLAYING})

        # Change to "Paused"
        self.player.set_player_state(PlayerState.PAUSED)
        self.assertEqual(self.player.state, PlayerState.PAUSED)
        self.assertEqual(self.player.gui["status"], "Paused")
        self.player.mpris.update_props.assert_called_with(
            {"CanPause": False, "CanPlay": True, "PlaybackStatus": "Paused"})
        last_message = self.emitted_msgs[-1]
        self.assertEqual(last_message.msg_type, "ovos.common_play.player.state")
        self.assertEqual(last_message.data, {"state": PlayerState.PAUSED})

        # Change to "Stopped"
        self.player.set_player_state(PlayerState.STOPPED)
        self.assertEqual(self.player.state, PlayerState.STOPPED)
        self.assertEqual(self.player.gui["status"], "Stopped")
        self.player.mpris.update_props.assert_called_with(
            {"CanPause": False, "CanPlay": False, "PlaybackStatus": "Stopped"})
        last_message = self.emitted_msgs[-1]
        self.assertEqual(last_message.msg_type, "ovos.common_play.player.state")
        self.assertEqual(last_message.data, {"state": PlayerState.STOPPED})

        # Request invalid change
        with self.assertRaises(TypeError):
            self.player.set_player_state("Paused")
        self.assertEqual(last_message, self.emitted_msgs[-1])
        self.assertEqual(self.player.state, PlayerState.STOPPED)

        with self.assertRaises(TypeError):
            self.player.set_player_state(2)
        self.assertEqual(last_message, self.emitted_msgs[-1])
        self.assertEqual(self.player.state, PlayerState.STOPPED)

        self.player.mpris.update_props = real_update_props

    def test_set_now_playing(self):
        real_update_props = self.player.mpris.update_props
        real_update_track = self.player.gui.update_current_track
        real_update_plist = self.player.gui.update_playlist
        real_nowplaying_reset = self.player.now_playing.reset

        self.player.mpris.update_props = Mock()
        self.player.gui.update_current_track = Mock()
        self.player.gui.update_playlist = Mock()
        self.player.now_playing.reset = Mock()

        valid_dict = valid_search_results[0]
        valid_track = MediaEntry.from_dict(valid_search_results[1])
        invalid_str = json.dumps(valid_search_results[2])
        track_no_uri = valid_search_results[2]
        track_no_uri.pop('uri')
        # TODO: Test playlist result

        # Play valid dict result
        self.player.set_now_playing(valid_dict)
        entry = MediaEntry.from_dict(valid_dict)
        # self.assertEqual(self.player.now_playing.as_dict, valid_dict)
        self.assertEqual(self.player.now_playing, entry)
        self.assertEqual(self.player.playlist.current_track, entry)
        self.assertEqual(self.player.playlist[-1], entry)
        self.player.gui.update_current_track.assert_called_once()
        self.player.gui.update_playlist.assert_called_once()
        self.player.mpris.update_props.assert_called_once_with(
            {"Metadata": self.player.now_playing.mpris_metadata}
        )
        self.player.now_playing.reset.assert_called_once()
        self.player.now_playing.reset.reset_mock()
        self.player.gui.update_current_track.reset_mock()
        self.player.gui.update_playlist.reset_mock()
        self.player.mpris.update_props.reset_mock()

        # Play valid MediaEntry result
        self.player.set_now_playing(valid_track)
        self.assertEqual(self.player.now_playing, valid_track)
        self.assertEqual(self.player.playlist.current_track, valid_track)
        self.assertEqual(self.player.playlist[-1], valid_track)
        self.player.gui.update_current_track.assert_called_once()
        self.player.gui.update_playlist.assert_called_once()
        self.player.mpris.update_props.assert_called_once_with(
            {"Metadata": self.player.now_playing.mpris_metadata})
        self.player.now_playing.reset.assert_called_once()
        self.player.now_playing.reset.reset_mock()
        self.player.gui.update_current_track.reset_mock()
        self.player.gui.update_playlist.reset_mock()
        self.player.mpris.update_props.reset_mock()

        # Play invalid string result
        with self.assertRaises(ValueError):
            self.player.set_now_playing(invalid_str)
        self.player.now_playing.reset.assert_not_called()
        self.player.gui.update_current_track.assert_not_called()
        self.player.gui.update_playlist.assert_not_called()
        self.player.mpris.update_props.assert_not_called()

        # Play result with no URI
        self.player.set_now_playing(track_no_uri)
        self.player.gui.update_current_track.assert_called_once()
        self.player.gui.update_playlist.assert_called_once()
        self.player.mpris.update_props.assert_called_once_with(
            {"Metadata": self.player.now_playing.mpris_metadata})
        self.player.now_playing.reset.assert_called_once()

        self.player.mpris.update_props = real_update_props
        self.player.gui.update_current_track = real_update_track
        self.player.gui.update_playlist = real_update_plist
        self.player.now_playing.reset = real_nowplaying_reset

    @patch("ovos_plugin_common_play.ocp.player.is_gui_running")
    def test_validate_stream(self, gui_running):
        real_update = self.player.gui.update_current_track
        self.player.gui.update_current_track = Mock()
        media_entry = MediaEntry.from_dict(valid_search_results[0])
        invalid_result = valid_search_results[1]
        invalid_result.pop('uri')
        invalid_entry = MediaEntry.from_dict(invalid_result)

        # Valid Entry
        self.player.now_playing.update(media_entry)

        self.assertFalse(self.player.now_playing.is_cps)
        self.assertEqual(self.player.now_playing.playback,
                         PlaybackType.AUDIO)
        self.assertEqual(self.player.active_backend, PlaybackType.AUDIO)

        # Test with GUI
        gui_running.return_value = True
        self.assertTrue(self.player.validate_stream())
        self.assertEqual(self.player.gui["stream"], media_entry.uri)
        self.player.gui.update_current_track.assert_called_once()
        self.assertEqual(self.player.now_playing.playback,
                         PlaybackType.AUDIO)

        # Invalid Entry
        self.player.now_playing.update(invalid_entry)
        self.assertFalse(self.player.validate_stream())
        self.assertEqual(self.player.gui["stream"], media_entry.uri)
        self.player.gui.update_current_track.assert_called_once()

        # Test without GUI
        gui_running.return_value = False
        self.player.gui.update_current_track.reset_mock()
        self.player.gui["stream"] = None
        self.player.now_playing.update(media_entry)
        self.assertTrue(self.player.validate_stream())
        self.assertEqual(self.player.gui["stream"], media_entry.uri)
        self.player.gui.update_current_track.assert_called_once()
        self.assertEqual(self.player.now_playing.playback,
                         PlaybackType.AUDIO_SERVICE)

        # TODO: Test Skill playback and non-audio playback
        self.player.gui.update_current_track = real_update

    def test_on_invalid_media(self):
        real_play_next = self.player.play_next
        real_show_error = self.player.gui.show_playback_error
        self.player.play_next = Mock()
        self.player.gui.show_playback_error = Mock()

        self.player.on_invalid_media()
        self.player.play_next.assert_called_once()
        self.player.gui.show_playback_error.assert_called_once()

        self.player.play_next = real_play_next
        self.player.gui.show_playback_error = real_show_error

    def test_play_media(self):
        real_stop = self.player.mpris.stop
        real_pause = self.player.pause
        real_gui_update = self.player.gui.update_search_results
        real_play = self.player.play
        real_set_now_playing = self.player.set_now_playing
        self.player.mpris.stop = Mock()
        self.player.pause = Mock()
        self.player.gui.update_search_results = Mock()
        self.player.play = Mock()
        self.player.set_now_playing = Mock()

        results_as_entries = [MediaEntry.from_dict(d)
                              for d in valid_search_results]
        results_as_entries.sort(key=lambda k: k.match_confidence, reverse=True)

        # Test invalid track
        with self.assertRaises(TypeError):
            self.player.play_media(valid_search_results)
        with self.assertRaises(TypeError):
            self.player.play_media(json.dumps(valid_search_results[0]))

        # Test track only
        self.player.state = PlayerState.STOPPED
        track = MediaEntry.from_dict(valid_search_results[0])
        self.player.play_media(track)
        self.player.mpris.stop.assert_called_once()
        self.player.pause.assert_not_called()
        self.assertEqual(self.player.media.search_playlist.entries, list())
        self.player.gui.update_search_results.assert_not_called()
        self.assertEqual(self.player.playlist.entries, list())
        self.player.set_now_playing.assert_called_once_with(track)
        self.player.play.assert_called_once()

        self.player.mpris.stop.reset_mock()
        self.player.set_now_playing.reset_mock()
        self.player.play.reset_mock()

        # Test track with disambiguation
        self.player.state = PlayerState.PAUSED
        track = MediaEntry.from_dict(valid_search_results[0])
        self.player.play_media(track, valid_search_results)
        self.player.mpris.stop.assert_called_once()
        self.player.pause.assert_not_called()

        self.assertEqual(self.player.media.search_playlist.entries,
                         results_as_entries)
        self.player.gui.update_search_results.assert_called_once()
        self.assertEqual(self.player.playlist.entries, list())
        self.player.set_now_playing.assert_called_once_with(track)
        self.player.play.assert_called_once()

        self.player.mpris.stop.reset_mock()
        self.player.set_now_playing.reset_mock()
        self.player.play.reset_mock()
        self.player.gui.update_search_results.reset_mock()

        # Test track with playlist
        self.player.state = PlayerState.PLAYING
        self.player.media.search_playlist.clear()
        track = MediaEntry.from_dict(valid_search_results[0])
        self.player.play_media(track, playlist=valid_search_results)
        self.player.mpris.stop.assert_called_once()
        self.player.pause.assert_called_once()

        self.assertEqual(self.player.media.search_playlist.entries, list())
        self.player.gui.update_search_results.assert_not_called()
        self.assertEqual(self.player.playlist.entries, results_as_entries)
        self.assertEqual(self.player.playlist.current_track, track)
        self.player.set_now_playing.assert_called_once_with(track)
        self.player.play.assert_called_once()

        self.player.set_now_playing = real_set_now_playing
        self.player.play = real_play
        self.player.gui.update_search_results = real_gui_update
        self.player.pause = real_pause
        self.player.mpris.stop = real_stop

    def test_get_preferred_audio_backend(self):
        preferred = self.player._get_preferred_audio_backend()
        self.assertIsInstance(preferred, str)
        self.assertIn(preferred,
                      ["ovos_common_play", "vlc", "mplayer", "simple"])

    @patch("ovos_plugin_common_play.ocp.player.is_gui_running")
    def test_play(self, gui_running):
        gui_running.return_value = True
        real_update_props = self.player.mpris.update_props
        real_stop = self.player.mpris.stop
        real_validate_stream = self.player.validate_stream
        real_show_player = self.player.gui.show_player
        real_invalid = self.player.on_invalid_media
        real_player_state = self.player.set_player_state
        real_audio_service_play = self.player.audio_service.play
        self.player.mpris.update_props = Mock()
        self.player.validate_stream = Mock(return_value=False)
        mpris_stop = self.player.mpris.stop_event
        self.player.mpris.stop = Mock()
        self.player.gui.show_player = Mock()
        self.player.on_invalid_media = Mock()
        self.player.track_history = dict()
        self.player.set_player_state = Mock()
        self.player.audio_service.play = Mock()

        # Test invalid stream
        self.player.play()
        self.player.mpris.stop.assert_called_once()
        self.player.validate_stream.assert_called_once()
        self.player.on_invalid_media.assert_called_once()
        self.player.gui.show_player.assert_not_called()

        self.player.validate_stream.reset_mock()
        self.player.validate_stream.return_value = True

        # Test invalid backend
        self.player.now_playing.playback = PlaybackType.UNDEFINED
        mpris_stop.set()
        with self.assertRaises(ValueError):
            self.player.play()
        self.player.validate_stream.assert_called_once()
        self.player.mpris.update_props.assert_not_called()

        # TODO: Should the GUI be displayed and track history updated for
        #       invalid playback requests?
        self.player.gui.show_player.assert_called_once()
        self.assertEqual(set(self.player.track_history.keys()), {''})

        self.player.gui.show_player.reset_mock()
        self.player.validate_stream.reset_mock()

        # Test valid audio with gui
        media = MediaEntry.from_dict(valid_search_results[0])
        media.playback = PlaybackType.AUDIO
        self.player.now_playing.update(media)
        mpris_stop.set()
        self.player.play()
        self.player.mpris.stop.assert_called_once()
        self.player.validate_stream.assert_called_once()
        self.player.on_invalid_media.assert_called_once()
        self.player.gui.show_player.assert_called_once()
        self.assertEqual(set(self.player.track_history.keys()), {'', media.uri})
        self.assertEqual(self.player.track_history[media.uri], 1)
        last_message = self.emitted_msgs[-1]
        second_last_message = self.emitted_msgs[-2]
        self.assertEqual(last_message.msg_type, "ovos.common_play.track.state")
        self.assertEqual(last_message.data, {"state": TrackState.PLAYING_AUDIO})
        self.assertEqual(second_last_message.msg_type,
                         "gui.player.media.service.play")
        self.assertEqual(second_last_message.data,
                         {"track": media.uri, "mime": list(media.mimetype),
                          "repeat": False})

        self.player.mpris.stop.reset_mock()
        self.player.validate_stream.reset_mock()
        self.player.gui.show_player.reset_mock()

        # Test valid audio without gui (AudioService)
        gui_running.return_value = False
        self.player.mpris.stop_event.clear()
        self.player.play()
        self.player.mpris.stop.assert_called_once()
        self.player.validate_stream.assert_called_once()
        self.player.on_invalid_media.assert_called_once()
        self.player.gui.show_player.assert_called_once()
        self.assertEqual(set(self.player.track_history.keys()), {'', media.uri})
        self.assertEqual(self.player.track_history[media.uri], 2)
        self.assertEqual(self.player.active_backend, PlaybackType.AUDIO_SERVICE)
        self.player.set_player_state.assert_called_once_with(
            PlayerState.PLAYING)
        self.player.audio_service.play.assert_called_once_with(
            media.uri, utterance=self.player.audio_service_player)
        last_message = self.emitted_msgs[-1]
        self.assertEqual(last_message.msg_type, "ovos.common_play.track.state")
        self.assertEqual(last_message.data,
                         {"state": TrackState.PLAYING_AUDIOSERVICE})

        # TODO: Test Skill, Video, Webview

        self.player.on_invalid_media = real_invalid
        self.player.gui.show_player = real_show_player
        self.player.mpris.stop = real_stop
        self.player.validate_stream = real_validate_stream
        self.player.mpris.update_props = real_update_props
        self.player.set_player_state = real_player_state
        self.player.audio_service.play = real_audio_service_play

    def test_play_shuffle(self):
        # TODO
        pass

    def test_play_next(self):
        real_mpris = self.player.mpris.play_next
        real_pause = self.player.pause
        real_play = self.player.play
        real_shuffle = self.player.play_shuffle
        real_gui_end = self.player.gui.handle_end_of_playback

        self.player.mpris.play_next = Mock()
        self.player.pause = Mock()
        self.player.play = Mock()
        self.player.play_shuffle = Mock()
        self.player.gui.handle_end_of_playback = Mock()

        # MPRIS Next
        self.player.now_playing.playback = PlaybackType.MPRIS
        self.player.play_next()
        self.player.mpris.play_next.assert_called_once()

        # Skill Next
        self.player.now_playing.playback = PlaybackType.SKILL
        self.player.play_next()
        last_message = self.emitted_msgs[-1]
        self.assertEqual(
            last_message.msg_type,
            f"ovos.common_play.{self.player.now_playing.skill_id}.next")

        # Repeat Track
        self.player.now_playing.playback = PlaybackType.AUDIO
        self.player.loop_state = LoopState.REPEAT_TRACK
        self.player.play_next()
        self.player.pause.assert_called_once()
        self.player.play.assert_called_once()

        # Shuffle
        self.player.pause.reset_mock()
        self.player.play.reset_mock()
        self.player.loop_state = LoopState.NONE
        self.player.shuffle = True
        self.player.play_next()
        self.player.pause.assert_called_once()
        self.player.play_shuffle.assert_called_once()
        self.player.play.assert_called_once()

        # Playlist next track
        self.player.pause.reset_mock()
        self.player.play.reset_mock()
        self.player.shuffle = False
        self.player.playlist.replace(valid_search_results)
        self.player.play_next()
        self.player.pause.assert_called_once()
        self.player.play.assert_called_once()
        self.assertEqual(self.player.now_playing, self.player.playlist[1])

        # Playlist repeat
        self.player.loop_state = LoopState.REPEAT
        self.player.playlist.set_position(len(self.player.playlist) - 1)
        self.player.pause.reset_mock()
        self.player.play.reset_mock()
        self.player.play_next()
        self.player.pause.assert_called_once()
        self.player.play.assert_called_once()
        self.assertTrue(self.player.playlist.is_first_track)

        # Playlist no repeat
        self.player.loop_state = LoopState.NONE
        self.player.playlist.set_position(len(self.player.playlist) - 1)
        self.player.pause.reset_mock()
        self.player.play.reset_mock()
        self.player.play_next()
        self.player.pause.assert_called_once()
        self.player.play.assert_not_called()
        self.player.gui.handle_end_of_playback.assert_called_once()

        # Search results next track
        self.player.gui.handle_end_of_playback.reset_mock()
        self.player.playlist.clear()
        self.player.media.search_playlist.replace(valid_search_results)
        self.assertEqual(len(self.player.playlist), 0)
        self.player.pause.reset_mock()
        self.player.play.reset_mock()
        self.player.play_next()
        self.player.pause.assert_called_once()
        self.player.play.assert_called_once()
        self.player.gui.handle_end_of_playback.assert_not_called()

        # Search results end
        self.player.pause.reset_mock()
        self.player.play.reset_mock()
        # TODO: should we repeat search results, or skip adding them to the playlist
        self.player.playlist.clear()
        self.player.media.search_playlist.set_position(
            len(self.player.media.search_playlist) - 1)
        self.assertTrue(self.player.media.search_playlist.is_last_track)
        self.assertEqual(len(self.player.playlist), 0)
        self.player.loop_state = LoopState.REPEAT
        self.player.play_next()
        self.player.pause.assert_called_once()
        self.player.play.assert_not_called()
        self.player.gui.handle_end_of_playback.assert_called_once()

        # TODO: Test with `merge_search` set to False

        self.player.mpris.play_next.assert_called_once()

        self.player.gui.handle_end_of_playback = real_gui_end
        self.player.play_shuffle = real_shuffle
        self.player.play = real_play
        self.player.pause = real_pause
        self.player.mpris.play_next = real_mpris

    def test_play_prev(self):
        # TODO
        pass

    def test_pause(self):
        real_audio_pause = self.player.audio_service.pause
        real_player_pause = self.player.mpris.pause
        real_player_state = self.player.set_player_state

        self.player.audio_service.pause = Mock()
        self.player.mpris.pause = Mock()
        self.player.set_player_state = Mock()

        # Test Audio service Pause
        self.player._paused_on_duck = True
        self.player.now_playing.playback = PlaybackType.AUDIO_SERVICE
        self.player.pause()
        self.player.audio_service.pause.assert_called_once()
        self.assertFalse(self.player._paused_on_duck)
        self.player.set_player_state.assert_called_once_with(PlayerState.PAUSED)

        # Test GUI Pause
        self.player.set_player_state.reset_mock()
        self.player._paused_on_duck = True
        self.player.now_playing.playback = PlaybackType.AUDIO
        self.player.pause()
        self.assertFalse(self.player._paused_on_duck)
        self.player.set_player_state.assert_called_once_with(PlayerState.PAUSED)
        last_message = self.emitted_msgs[-1]
        self.assertEqual(last_message.msg_type,
                         "gui.player.media.service.pause")

        # Test Skill Pause
        self.player.set_player_state.reset_mock()
        self.player._paused_on_duck = True
        self.player.now_playing.playback = PlaybackType.SKILL
        self.player.pause()
        self.assertFalse(self.player._paused_on_duck)
        self.player.set_player_state.assert_called_once_with(PlayerState.PAUSED)
        last_message = self.emitted_msgs[-1]
        self.assertEqual(last_message.msg_type,
                         f"ovos.common_play.{self.player.active_skill}.pause")

        # Test MPRIS Pause
        self.player.set_player_state.reset_mock()
        self.player._paused_on_duck = True
        self.player.now_playing.playback = PlaybackType.MPRIS
        self.player.pause()
        self.assertFalse(self.player._paused_on_duck)
        self.player.set_player_state.assert_called_once_with(PlayerState.PAUSED)
        self.player.mpris.pause.assert_called_once()

        # TODO: Test Undefined playback

        self.player.audio_service.pause.assert_called_once()

        self.player.audio_service.pause = real_audio_pause
        self.player.mpris.pause = real_player_pause
        self.player.set_player_state = real_player_state

    def test_resume(self):
        real_audio_resume = self.player.audio_service.resume
        real_player_resume = self.player.mpris.resume
        real_player_state = self.player.set_player_state

        self.player.audio_service.resume = Mock()
        self.player.mpris.resume = Mock()
        self.player.set_player_state = Mock()

        # Test Audio service Resume
        self.player.now_playing.playback = PlaybackType.AUDIO_SERVICE
        self.player.resume()
        self.player.audio_service.resume.assert_called_once()
        self.player.set_player_state.assert_called_once_with(PlayerState.PLAYING)

        # Test GUI Resume
        self.player.set_player_state.reset_mock()
        self.player.now_playing.playback = PlaybackType.AUDIO
        self.player.resume()
        self.player.set_player_state.assert_called_once_with(PlayerState.PLAYING)
        last_message = self.emitted_msgs[-1]
        self.assertEqual(last_message.msg_type,
                         "gui.player.media.service.resume")

        # Test Skill Resume
        self.player.set_player_state.reset_mock()
        self.player.now_playing.playback = PlaybackType.SKILL
        self.player.resume()
        self.player.set_player_state.assert_called_once_with(PlayerState.PLAYING)
        last_message = self.emitted_msgs[-1]
        self.assertEqual(last_message.msg_type,
                         f"ovos.common_play.{self.player.active_skill}.resume")

        # Test MPRIS Resume
        self.player.set_player_state.reset_mock()
        self.player.now_playing.playback = PlaybackType.MPRIS
        self.player.resume()
        self.player.set_player_state.assert_called_once_with(PlayerState.PLAYING)
        self.player.mpris.resume.assert_called_once()

        # TODO: Test Undefined playback

        self.player.audio_service.resume.assert_called_once()

        self.player.audio_service.resume = real_audio_resume
        self.player.mpris.resume = real_player_resume
        self.player.set_player_state = real_player_state

    def test_seek(self):
        real_method = self.player.audio_service.set_track_position
        mock_method = Mock()
        self.player.audio_service.set_track_position = mock_method

        # Audio Service
        self.player.now_playing.playback = PlaybackType.AUDIO_SERVICE
        test_pos = 1234
        self.player.seek(test_pos)
        mock_method.assert_called_once_with(1.234)
        self.assertEqual(self.player.gui["position"], test_pos)

        # Audio
        self.player.now_playing.playback = PlaybackType.AUDIO
        test_pos = 10000
        self.player.seek(test_pos)
        mock_method.assert_called_once_with(1.234)
        self.assertEqual(self.player.gui["position"], test_pos)

        # Undefined
        self.player.now_playing.playback = PlaybackType.UNDEFINED
        test_pos = 999
        self.player.seek(test_pos)
        mock_method.assert_called_with(0.999)
        self.assertEqual(self.player.gui["position"], test_pos)

        self.player.audio_service.set_track_position = real_method

    def test_stop(self):
        # TODO
        pass

    def test_stop_gui_player(self):
        self.player.stop_gui_player()
        message = self.emitted_msgs[-1]
        self.assertEqual(message.msg_type, "gui.player.media.service.stop")

    def test_stop_audio_skill(self):
        self.player.stop_audio_skill()
        message = self.emitted_msgs[-1]
        self.assertEqual(message.msg_type,
                         f"ovos.common_play.{self.player.active_skill}.stop")

    def test_stop_audio_service(self):
        real_stop = self.player.audio_service.stop
        self.player.audio_service.stop = Mock()
        self.player.stop_audio_service()
        self.player.audio_service.stop.assert_called_once()

        self.player.audio_service.stop = real_stop

    def test_reset(self):
        real_stop = self.player.stop
        self.player.stop = Mock()

        self.player.reset()
        self.player.stop.assert_called_once()
        self.assertEqual(self.player.playlist.entries, list())
        self.assertIsNone(self.player.playlist.current_track)
        self.assertEqual(self.player.media.search_playlist, list())
        self.assertEqual(self.player.media_state, MediaState.NO_MEDIA)
        # TODO: Should this update player state?
        # self.assertEqual(self.player.state, PlayerState.STOPPED)
        self.assertFalse(self.player.shuffle)
        self.assertEqual(self.player.loop_state, LoopState.NONE)

        self.player.stop = real_stop

    def test_shutdown(self):
        # TODO
        pass

    def test_handle_player_state_update(self):
        real_view_timeout = self.player.gui.cancel_app_view_timeout
        real_pause_timeout = self.player.gui.schedule_app_view_pause_timeout
        real_update_props = self.player.mpris.update_props
        view_timeout = Mock()
        view_pause = Mock()
        update_props = Mock()
        self.player.gui.cancel_app_view_timeout = view_timeout
        self.player.gui.schedule_app_view_pause_timeout = view_pause
        self.player.mpris.update_props = update_props

        self.player.settings['app_view_timeout_mode'] = "pause"
        self.player.settings['app_view_timeout_enabled'] = False

        # Invalid requests
        with self.assertRaises(ValueError):
            self.player.handle_player_state_update(
                Message("", {"not_state": None}))
        with self.assertRaises(ValueError):
            self.player.handle_player_state_update(
                Message("", {"state": None}))
        with self.assertRaises(ValueError):
            self.player.handle_player_state_update(
                Message("", {"state": "Playing"}))
        view_timeout.assert_not_called()
        view_pause.assert_not_called()
        update_props.assert_not_called()

        # State not changed
        self.player.state = PlayerState.PLAYING
        self.player.handle_player_state_update(
            Message("", {"state": PlayerState.PLAYING}))
        self.player.handle_player_state_update(
            Message("", {"state": int(PlayerState.PLAYING)}))
        view_timeout.assert_not_called()
        view_pause.assert_not_called()
        update_props.assert_not_called()
        self.assertEqual(self.player.state, PlayerState.PLAYING)

        # Pause no GUI change
        self.player.handle_player_state_update(
            Message("", {"state": PlayerState.PAUSED}))
        view_timeout.assert_not_called()
        view_pause.assert_not_called()
        update_props.assert_called_with({"CanPause": False,
                                         "CanPlay": True,
                                         "PlaybackStatus": "Paused"})
        self.assertEqual(self.player.state, PlayerState.PAUSED)

        # Play
        self.player.handle_player_state_update(
            Message("", {"state": PlayerState.PLAYING}))
        view_timeout.assert_not_called()
        view_pause.assert_not_called()
        update_props.assert_called_with({"CanPause": True,
                                         "CanPlay": False,
                                         "PlaybackStatus": "Playing"})
        self.assertEqual(self.player.state, PlayerState.PLAYING)

        # Pause with GUI Change
        self.player.settings['app_view_timeout_enabled'] = True
        self.player.handle_player_state_update(
            Message("", {"state": PlayerState.PAUSED}))
        view_timeout.assert_called_once()
        view_pause.assert_called_once()
        update_props.assert_called_with({"CanPause": False,
                                         "CanPlay": True,
                                         "PlaybackStatus": "Paused"})
        self.assertEqual(self.player.state, PlayerState.PAUSED)

        # Stop
        self.player.handle_player_state_update(
            Message("", {"state": PlayerState.STOPPED}))
        view_timeout.assert_called_once()
        view_pause.assert_called_once()
        update_props.assert_called_with({"CanPause": False,
                                         "CanPlay": False,
                                         "PlaybackStatus": "Stopped"})
        self.assertEqual(self.player.state, PlayerState.STOPPED)

        self.player.gui.cancel_app_view_timeout = real_view_timeout
        self.player.gui.schedule_app_view_pause_timeout = real_pause_timeout
        self.player.mpris.update_props = real_update_props

    def test_handle_player_media_update(self):
        real_handle_playback_ended = self.player.handle_playback_ended
        real_handle_invalid_media = self.player.handle_invalid_media
        real_play_next = self.player.play_next

        self.player.play_next = Mock()
        self.player.handle_playback_ended = Mock()
        self.player.handle_invalid_media = Mock()
        self.player.media_state = MediaState.UNKNOWN

        # Invalid requests
        with self.assertRaises(ValueError):
            self.player.handle_player_media_update(
                Message("", {"not_state": None}))
        with self.assertRaises(ValueError):
            self.player.handle_player_media_update(
                Message("", {"state": None}))
        with self.assertRaises(ValueError):
            self.player.handle_player_media_update(
                Message("", {"state": "UNKNOWN"}))
        self.player.handle_playback_ended.assert_not_called()
        self.player.handle_invalid_media.assert_not_called()
        self.assertEqual(self.player.media_state, MediaState.UNKNOWN)

        # State not changed
        self.player.handle_player_media_update(
            Message("", {"state": MediaState.UNKNOWN}))
        self.assertEqual(self.player.media_state, MediaState.UNKNOWN)
        self.player.handle_player_media_update(
            Message("", {"state": 0}))
        self.assertEqual(self.player.media_state, MediaState.UNKNOWN)
        self.player.handle_playback_ended.assert_not_called()
        self.player.handle_invalid_media.assert_not_called()
        self.player.play_next.assert_not_called()

        # Valid state changes
        self.player.handle_player_media_update(
            Message("", {"state": MediaState.NO_MEDIA}))
        self.assertEqual(self.player.media_state, MediaState.NO_MEDIA)
        self.player.handle_player_media_update(
            Message("", {"state": MediaState.LOADING_MEDIA}))
        self.assertEqual(self.player.media_state, MediaState.LOADING_MEDIA)
        self.player.handle_player_media_update(
            Message("", {"state": MediaState.STALLED_MEDIA}))
        self.assertEqual(self.player.media_state, MediaState.STALLED_MEDIA)
        self.player.handle_player_media_update(
            Message("", {"state": MediaState.BUFFERING_MEDIA}))
        self.assertEqual(self.player.media_state, MediaState.BUFFERING_MEDIA)
        self.player.handle_player_media_update(
            Message("", {"state": MediaState.BUFFERED_MEDIA}))
        self.assertEqual(self.player.media_state, MediaState.BUFFERED_MEDIA)
        self.player.handle_playback_ended.assert_not_called()
        self.player.handle_invalid_media.assert_not_called()
        self.player.play_next.assert_not_called()

        self.player.handle_player_media_update(
            Message("", {"state": MediaState.END_OF_MEDIA}))
        self.assertEqual(self.player.media_state, MediaState.END_OF_MEDIA)
        self.player.handle_playback_ended.assert_called_once()
        self.player.handle_invalid_media.assert_not_called()
        self.player.play_next.assert_not_called()

        self.player.handle_player_media_update(
            Message("", {"state": MediaState.INVALID_MEDIA}))
        self.assertEqual(self.player.media_state, MediaState.INVALID_MEDIA)
        self.player.handle_playback_ended.assert_called_once()
        self.player.handle_invalid_media.assert_called_once()
        self.player.play_next.assert_called_once()
        # TODO: Test without autoplay

        self.player.play_next = real_play_next
        self.player.handle_playback_ended = real_handle_playback_ended
        self.player.handle_invalid_media = real_handle_invalid_media

    def test_handle_invalid_media(self):
        # TODO
        pass

    def test_handle_playback_ended(self):
        # TODO
        pass

    def test_handle_play_request(self):
        # TODO
        pass

    def test_handle_pause_request(self):
        # TODO
        pass

    def test_handle_stop_request(self):
        # TODO
        pass

    def test_handle_resume_request(self):
        # TODO
        pass

    def test_handle_seek_request(self):
        # TODO
        pass

    def test_handle_next_request(self):
        # TODO
        pass

    def test_handle_prev_request(self):
        # TODO
        pass

    def test_handle_set_shuffle(self):
        # TODO
        pass

    def test_handle_unset_shuffle(self):
        # TODO
        pass

    def test_handle_set_repeat(self):
        # TODO
        pass

    def test_handle_unset_repeat(self):
        # TODO
        pass

    def test_handle_repeat_toggle_request(self):
        # TODO
        pass

    def test_handle_shuffle_toggle_request(self):
        # TODO
        pass

    def test_handle_playlist_set_request(self):
        # TODO
        pass

    def test_handle_playlist_queue_request(self):
        # TODO
        pass

    def test_handle_playlist_clear_request(self):
        # TODO
        pass

    def test_handle_duck_request(self):
        real_pause = self.player.pause
        self.player.pause = Mock()

        # Duck already paused
        self.player._paused_on_duck = False
        self.player.state = PlayerState.PAUSED
        self.player.handle_duck_request(None)
        self.player.pause.assert_not_called()
        self.assertFalse(self.player._paused_on_duck)

        # Duck while stopped
        self.player.state = PlayerState.STOPPED
        self.player.handle_duck_request(None)
        self.player.pause.assert_not_called()
        self.assertFalse(self.player._paused_on_duck)

        # Duck while playing
        self.player.state = PlayerState.PLAYING
        self.player.handle_duck_request(None)
        self.player.pause.assert_called_once()
        self.assertTrue(self.player._paused_on_duck)

        self.player.pause = real_pause

    def test_handle_unduck_request(self):
        real_resume = self.player.resume
        self.player.resume = Mock()
        self.player._paused_on_duck = False

        # Unduck already playing
        self.player.state = PlayerState.PLAYING
        self.player.handle_unduck_request(None)
        self.player.resume.assert_not_called()
        self.assertFalse(self.player._paused_on_duck)

        # Unduck while stopped
        self.player.state = PlayerState.STOPPED
        self.player.handle_unduck_request(None)
        self.player.resume.assert_not_called()
        self.assertFalse(self.player._paused_on_duck)

        # Unduck paused (not from duck)
        self.player.state = PlayerState.PAUSED
        self.player.handle_unduck_request(None)
        self.player.resume.assert_not_called()
        self.assertFalse(self.player._paused_on_duck)

        # Unduck paused on duck
        self.player._paused_on_duck = True
        self.player.state = PlayerState.PAUSED
        self.player.handle_unduck_request(None)
        self.player.resume.assert_called_once()
        self.assertFalse(self.player._paused_on_duck)

        self.player.resume = real_resume

    def test_handle_track_length_request(self):
        # TODO
        pass

    def test_handle_track_position_request(self):
        # TODO
        pass

    def test_handle_set_track_position_request(self):
        # TODO
        pass

    def test_handle_track_info_request(self):
        # TODO
        pass

    def test_handle_list_backends_request(self):
        # TODO
        pass

    def test_handle_enable_app_timeout(self):
        # TODO
        pass

    def test_handle_set_app_timeout(self):
        # TODO
        pass

    def test_handle_set_app_timeout_mode(self):
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
