import json
import unittest

from ovos_bus_client import Message
from ovos_utils.messagebus import FakeBus
from unittest.mock import Mock, MagicMock

from ovos_plugin_common_play.ocp import OCP
from ovos_plugin_common_play.ocp.status import MediaType, PlayerState


class TestOCP(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
