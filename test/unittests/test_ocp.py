import json
import unittest

from mycroft_bus_client import Message
from ovos_utils.messagebus import FakeBus
from unittest.mock import Mock, MagicMock

from ovos_plugin_common_play import PlayerState
from ovos_plugin_common_play.ocp.status import MediaType, LoopState, MediaState, PlaybackType


class TestOCP(unittest.TestCase):
    from ovos_plugin_common_play import OCP
    bus = FakeBus()
    ocp = OCP(bus)

    @classmethod
    def setUpClass(cls) -> None:
        cls.bus.emitted_msgs = []

        def get_msg(msg):
            msg = json.loads(msg)
            msg.pop("context")
            cls.bus.emitted_msgs.append(msg)

        cls.bus.on("message", get_msg)

    def test_00_ocp_init(self):
        from ovos_plugin_common_play.ocp.player import OCPMediaPlayer
        from ovos_plugin_common_play.ocp.gui import OCPMediaPlayerGUI
        from ovos_workshop.app import OVOSAbstractApplication
        self.assertIsInstance(self.ocp, OVOSAbstractApplication)
        self.assertIsInstance(self.ocp.gui, OCPMediaPlayerGUI)
        self.assertIsInstance(self.ocp.settings, dict)
        self.assertIsInstance(self.ocp.player, OCPMediaPlayer)
        self.assertIsNotNone(self.ocp.media_intents)

        # Mock startup events
        def _handle_skills_check(msg):
            self.bus.emit(msg.response(data={'status': True}))

        self.bus.once('mycroft.skills.is_ready', _handle_skills_check)
        self.bus.emit(Message('mycroft.ready'))

        self.assertTrue(self.ocp._intents_event.is_set())

        # TODO: Test messagebus event registration

    def test_ping(self):
        resp = self.bus.wait_for_response(Message("ovos.common_play.ping"),
                                          reply_type="ovos.common_play.pong")
        self.assertIsInstance(resp, Message)

    def test_handle_home(self):
        real_gui_home = self.ocp.gui.show_home
        self.ocp.gui.show_home = Mock()
        self.ocp.handle_home()
        self.ocp.gui.show_home.assert_called_once_with(app_mode=True)
        self.ocp.gui.show_home = real_gui_home

    def test_register_ocp_events(self):
        # TODO
        pass

    def test_register_media_events(self):
        # TODO
        pass

    def test_replace_mycroft_cps(self):
        # TODO
        pass

    def test_default_shutdown(self):
        # TODO
        pass

    def test_classify_media(self):
        music = "play some music"
        movie = "play a movie"
        news = "play the latest news"
        unknown = "play something"

        self.assertEqual(self.ocp.classify_media(music), MediaType.MUSIC)
        self.assertEqual(self.ocp.classify_media(movie), MediaType.MOVIE)
        self.assertEqual(self.ocp.classify_media(news), MediaType.NEWS)
        self.assertEqual(self.ocp.classify_media(unknown), MediaType.GENERIC)

    def test_handle_open(self):
        real_gui_home = self.ocp.gui.show_home
        self.ocp.gui.show_home = Mock()
        self.ocp.handle_open(None)
        self.ocp.gui.show_home.assert_called_once_with(app_mode=True)
        self.ocp.gui.show_home = real_gui_home

    def test_handle_playback_intents(self):
        real_player = self.ocp.player
        self.ocp.player = MagicMock()

        # next
        self.ocp.handle_next(None)
        self.ocp.player.play_next.assert_called_once()

        # previous
        self.ocp.handle_prev(None)
        self.ocp.player.play_prev.assert_called_once()

        # pause
        self.ocp.handle_pause(None)
        self.ocp.player.pause.assert_called_once()

        # stop
        self.ocp.handle_stop()
        self.ocp.player.stop.assert_called_once()

        # resume
        self.ocp.player.state = PlayerState.PAUSED
        self.ocp.handle_resume(None)
        self.ocp.player.resume.assert_called_once()

        # resume while playing
        self.ocp.player.state = PlayerState.PLAYING
        real_get_response = self.ocp.get_response
        real_play = self.ocp.handle_play
        self.ocp.get_response = Mock(return_value="test")
        self.ocp.handle_play = Mock()

        test_message = Message("test")
        self.ocp.handle_resume(test_message)
        self.ocp.get_response.assert_called_once_with("play.what")
        self.ocp.handle_play.assert_called_once_with(test_message)
        self.assertEqual(test_message.data['utterance'], 'test')

        self.ocp.handle_play = real_play
        self.ocp.get_response = real_get_response
        self.ocp.player = real_player

    def test_handle_play(self):
        # TODO
        pass

    def test_handle_read(self):
        # TODO
        pass

    def test_do_play(self):
        # TODO
        pass

    def test_search(self):
        # TODO
        pass

    def test_should_resume(self):
        valid_utt = "resume"
        invalid_utt = "test"
        empty_utt = ""

        # Playing
        self.ocp.player.state = PlayerState.PLAYING
        self.assertFalse(self.ocp._should_resume(valid_utt))
        self.assertFalse(self.ocp._should_resume(invalid_utt))
        self.assertFalse(self.ocp._should_resume(empty_utt))

        # Stopped
        self.ocp.player.state = PlayerState.STOPPED
        self.assertFalse(self.ocp._should_resume(valid_utt))
        self.assertFalse(self.ocp._should_resume(invalid_utt))
        self.assertFalse(self.ocp._should_resume(empty_utt))

        # Paused
        self.ocp.player.state = PlayerState.PAUSED
        self.assertTrue(self.ocp._should_resume(valid_utt))
        self.assertFalse(self.ocp._should_resume(invalid_utt))
        self.assertTrue(self.ocp._should_resume(empty_utt))


class TestOCPPlayer(unittest.TestCase):
    from ovos_plugin_common_play.ocp.player import OCPMediaPlayer
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
        from ovos_plugin_common_play.ocp.mycroft_cps import MycroftAudioService
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
        self.assertIsInstance(self.player.audio_service, MycroftAudioService)

        # TODO: Test messagebus event registration

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
        # TODO
        pass

    def test_validate_stream(self):
        # TODO
        pass

    def test_on_invalid_media(self):
        # TODO
        pass

    def test_play_media(self):
        # TODO
        pass

    def test_get_preferred_audio_backend(self):
        # TODO
        pass

    def test_play(self):
        # TODO
        pass

    def test_play_shuffle(self):
        # TODO
        pass

    def test_play_next(self):
        # TODO
        pass

    def test_play_prev(self):
        # TODO
        pass

    def test_pause(self):
        # TODO
        pass

    def test_resume(self):
        # TODO
        pass

    def test_seek(self):
        # TODO
        pass

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
        # TODO
        pass

    def test_shutdown(self):
        # TODO
        pass

    def test_handle_player_state_update(self):
        # TODO
        pass

    def test_handle_player_media_update(self):
        # TODO
        pass

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
        # TODO
        pass

    def test_handle_unduck_request(self):
        # TODO
        pass

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
