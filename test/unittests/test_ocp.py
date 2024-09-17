import json
import unittest

from ovos_bus_client import Message
from ovos_utils.messagebus import FakeBus
from unittest.mock import Mock, MagicMock

from ovos_plugin_common_play.ocp import OCP
from ovos_plugin_common_play.ocp.status import MediaType, PlayerState


class TestOCP(unittest.TestCase):
    bus = FakeBus()
    ocp = OCP(bus=bus, skill_id="TEST_OCP")

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

        # Mock startup events
        def _handle_skills_check(msg):
            self.bus.emit(msg.response(data={'status': True}))

        self.bus.once('mycroft.skills.is_ready', _handle_skills_check)
        self.bus.emit(Message('mycroft.ready'))

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

    def test_default_shutdown(self):
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
