import json
import unittest
from unittest.mock import patch

from mycroft.audio.audioservice import AudioService
from mycroft.configuration import Configuration
from ovos_utils.messagebus import FakeBus

BASE_CONF = {"Audio":
    {
        "native_sources": ["debug_cli", "audio"],
        "default-backend": "OCP",  # only used by mycroft-core
        "preferred_audio_services": ["ovos_test", "mycroft_test"],
        "backends": {
            "OCP": {
                "type": "ovos_common_play",
                "active": True,
                "mode": "external",
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


class TestExternalOCP(unittest.TestCase):

    @classmethod
    @patch.dict(Configuration._Configuration__patch, BASE_CONF)
    def setUpClass(self) -> None:
        self.bus = FakeBus()
        self.bus.emitted_msgs = []

        def get_msg(msg):
            msg = json.loads(msg)
            msg.pop("context")
            self.bus.emitted_msgs.append(msg)

        self.bus.on("message", get_msg)

        self.audio = AudioService(self.bus)

    def test_external_ocp(self):
        # assert that ocp is in external mode
        self.assertEqual(self.audio.default.config["mode"], "external")
        # assert that OCP is not loaded
        self.assertTrue(self.audio.default.ocp is None)

    def tearDown(self) -> None:
        self.audio.shutdown()


if __name__ == '__main__':
    unittest.main()
