import time
import unittest
from threading import Event
from unittest.mock import patch

from ovos_bus_client import Message
from ovos_utils.fakebus import FakeBus

from ovos_plugin_common_play.ocp.player import OCPMediaPlayer
from ovos_plugin_common_play.ocp.status import MediaType, PlaybackType

GRACE = 0.1

track = {'media_type': MediaType.MUSIC,
         'playback': PlaybackType.AUDIO,
         'uri': 'https://example.com/track.mp3',
         'title': 'Track',
         'match_confidence': 65}


@patch("ovos_plugin_common_play.ocp.gui.SEARCH_SPINNER_GRACE_SECONDS", GRACE)
class TestSearchSpinner(unittest.TestCase):
    def setUp(self):
        self.bus = FakeBus()
        self.player = OCPMediaPlayer(self.bus,
                                     settings={'disable_mpris': True})
        self.busy_removed = Event()

        def on_page_delete(message):
            if "busy" in message.data.get("page_names", []):
                self.busy_removed.set()

        self.bus.on("gui.page.delete", on_page_delete)

    def tearDown(self):
        self.player.shutdown()

    def test_spinner_removed_when_search_ends_without_playback(self):
        # pipeline found nothing: search.end, reset, "cant.play", no play request
        self.bus.emit(Message("ovos.common_play.search.start"))
        self.bus.emit(Message("ovos.common_play.search.end"))
        self.bus.emit(Message("ovos.common_play.reset"))
        self.assertTrue(self.busy_removed.wait(GRACE * 20))

    def test_spinner_kept_until_player_when_playback_follows(self):
        # successful search: a play request arrives right after search.end;
        # the spinner must stay up (stream extraction) until show_player()
        self.bus.emit(Message("ovos.common_play.search.start"))
        self.bus.emit(Message("ovos.common_play.search.end"))
        with patch.object(self.player, "play") as play:
            self.bus.emit(Message("ovos.common_play.play", {"media": track}))
        play.assert_called_once()
        time.sleep(GRACE * 3)
        self.assertFalse(self.busy_removed.is_set())

    def test_new_search_cancels_pending_removal(self):
        self.bus.emit(Message("ovos.common_play.search.start"))
        self.bus.emit(Message("ovos.common_play.search.end"))
        self.bus.emit(Message("ovos.common_play.search.start"))
        time.sleep(GRACE * 3)
        self.assertFalse(self.busy_removed.is_set())


if __name__ == "__main__":
    unittest.main()
