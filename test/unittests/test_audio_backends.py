import json
import unittest
from unittest.mock import patch

from ovos_audio.service import AudioService
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
                "mode": "auto",
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

    def tearDown(self) -> None:
        self.audio.shutdown()


if __name__ == '__main__':
    unittest.main()
