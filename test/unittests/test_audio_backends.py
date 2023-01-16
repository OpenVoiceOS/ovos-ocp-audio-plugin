import json
import unittest
from unittest.mock import patch

from mycroft.audio.audioservice import AudioService
from ovos_config.config import Configuration
from ovos_utils.messagebus import FakeBus

from ovos_plugin_common_play import OCPAudioBackend, OCP

BASE_CONF = {"Audio":
    {
        "native_sources": ["debug_cli", "audio"],
        "default-backend": "OCP",  # only used by mycroft-core
        "preferred_audio_services": ["ovos_test", "mycroft_test"],
        "backends": {
            "OCP": {
                "type": "ovos_common_play",
                "active": True,
                "mode": "local",
                "disable_mpris": True
            },
            "mycroft_test": {
                "type": "mycroft_test",
                "active": True
            },
            "ovos_test": {
                "type": "ovos_test",
                "active": True
            }
        }
    }
}


class TestOCPLoad(unittest.TestCase):

    @classmethod
    @patch.object(Configuration, 'load_all_configs')
    def setUpClass(self, mock_get) -> None:
        mock_get.return_value = BASE_CONF
        self.bus = FakeBus()
        self.bus.emitted_msgs = []

        def get_msg(msg):
            msg = json.loads(msg)
            msg.pop("context")
            self.bus.emitted_msgs.append(msg)

        self.bus.on("message", get_msg)

        self.audio = AudioService(self.bus)

    def test_native_ocp(self):
        # assert that OCP is the selected default backend
        self.assertTrue(isinstance(self.audio.default, OCPAudioBackend))

        # assert that OCP is in "local" mode
        self.assertEqual(self.audio.default.config["mode"], "local")

        # assert that OCP is loaded
        self.assertTrue(self.audio.default.ocp is not None)
        self.assertTrue(isinstance(self.audio.default.ocp, OCP))

        # assert that test backends also loaded
        # NOTE: "service" is a list, should be named "services"
        # not renamed for backwards compat but its a typo!
        loaded_services = [s.name for s in self.audio.service]
        self.assertIn("mycroft_test", loaded_services)
        self.assertIn("ovos_test", loaded_services)

    def tearDown(self) -> None:
        self.audio.shutdown()


if __name__ == '__main__':
    unittest.main()
