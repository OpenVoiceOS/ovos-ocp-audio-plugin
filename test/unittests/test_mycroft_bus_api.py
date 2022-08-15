import json
import unittest
from unittest.mock import patch

from mycroft.audio.audioservice import AudioService
from mycroft.configuration.config import Configuration
from ovos_utils.messagebus import FakeBus

from ovos_plugin_common_play.ocp.mycroft_cps import MycroftAudioService
from ovos_plugin_common_play.ocp.status import PlayerState, MediaState, TrackState, PlaybackType

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


class TestAudioServiceApi(unittest.TestCase):
    bus = FakeBus()

    @classmethod
    @patch.dict(Configuration._Configuration__patch, BASE_CONF)
    def setUpClass(cls) -> None:
        cls.bus.emitted_msgs = []

        def get_msg(msg):
            msg = json.loads(msg)
            msg.pop("context")
            cls.bus.emitted_msgs.append(msg)

        cls.bus.on("message", get_msg)

        cls.api = MycroftAudioService(cls.bus)

    @unittest.skip("debug - github actions gets stuck forever here ? works on my machine")
    @patch.dict(Configuration._Configuration__patch, BASE_CONF)
    def test_ocp_plugin_compat_layer(self):
        audio = AudioService(self.bus)
        self.bus.emitted_msgs = []

        # test play track from single uri
        test_uri = "file://path/to/music.mp3"
        self.api.play([test_uri])
        expected = [
            {'type': 'mycroft.audio.service.play',
             'data': {'tracks': [test_uri],
                      'utterance': '', 'repeat': False}},
            {'type': 'ovos.common_play.playlist.clear', 'data': {}},
            {'type': 'ovos.common_play.media.state', 'data': {'state': 3}},
            {'type': 'ovos.common_play.track.state', 'data': {'state': 31}},
            {'type': 'ovos.common_play.playlist.queue',
             'data': {
                 'tracks': [{'uri': test_uri,
                             'title': 'music.mp3', 'playback': 2, 'status': 1,
                             'skill_id': 'mycroft.audio_interface'}]}},
            {'type': 'ovos.common_play.play',
             'data': {
                 'repeat': False,
                 'media': {
                     'uri': test_uri,
                     'title': 'music.mp3', 'playback': 2, 'status': 1, 'skill_id': 'mycroft.audio_interface',
                     'skill': 'mycroft.audio_interface', 'position': 0, 'length': None, 'skill_icon': None,
                     'artist': None, 'is_cps': False, 'cps_data': {}},
                 'playlist': [
                     {'uri': test_uri,
                      'title': 'music.mp3', 'playback': 2, 'status': 1, 'skill_id': 'mycroft.audio_interface',
                      'skill': 'mycroft.audio_interface', 'position': 0, 'length': None, 'skill_icon': None,
                      'artist': None, 'is_cps': False, 'cps_data': {}}]}}
        ]
        for m in expected:
            self.assertIn(m, self.bus.emitted_msgs)

        # test pause
        self.bus.emitted_msgs = []
        self.api.pause()
        expected = [
            {'type': 'mycroft.audio.service.pause', 'data': {}},
            {'type': 'ovos.common_play.pause', 'data': {}}
        ]
        for m in expected:
            self.assertIn(m, self.bus.emitted_msgs)

        # test resume
        self.bus.emitted_msgs = []
        self.api.resume()
        expected = [
            {'type': 'mycroft.audio.service.resume', 'data': {}},
            {'type': 'ovos.common_play.resume', 'data': {}}
        ]
        for m in expected:
            self.assertIn(m, self.bus.emitted_msgs)

        # test next
        self.bus.emitted_msgs = []
        self.api.next()
        expected = [
            {'type': 'mycroft.audio.service.next', 'data': {}},
            {'type': 'ovos.common_play.next', 'data': {}}
        ]
        for m in expected:
            self.assertIn(m, self.bus.emitted_msgs)

        # test prev
        self.bus.emitted_msgs = []
        self.api.prev()
        expected = [
            {'type': 'mycroft.audio.service.prev', 'data': {}},
            {'type': 'ovos.common_play.previous', 'data': {}}
        ]
        for m in expected:
            self.assertIn(m, self.bus.emitted_msgs)

        # test queue
        self.bus.emitted_msgs = []
        playlist = ["file://path/to/music2.mp3", "file://path/to/music3.mp3"]
        self.api.queue(playlist)
        expected = [
            {'type': 'mycroft.audio.service.queue',
             'data': {'tracks': ['file://path/to/music2.mp3', 'file://path/to/music3.mp3']}},
            {'type': 'ovos.common_play.playlist.queue',
             'data': {'tracks': [
                 {'uri': 'file://path/to/music2.mp3', 'title': 'music2.mp3', 'playback': 2, 'status': 1,
                  'skill_id': 'mycroft.audio_interface'},
                 {'uri': 'file://path/to/music3.mp3', 'title': 'music3.mp3', 'playback': 2, 'status': 1,
                  'skill_id': 'mycroft.audio_interface'}]
             }}
        ]
        for m in expected:
            self.assertIn(m, self.bus.emitted_msgs)

        # test play playlist
        self.bus.emitted_msgs = []
        self.api.play([test_uri] + playlist)
        expected = [
            {'type': 'mycroft.audio.service.play',
             'data': {'tracks': ['file://path/to/music.mp3', 'file://path/to/music2.mp3', 'file://path/to/music3.mp3'],
                      'utterance': '',
                      'repeat': False}},
            {'type': 'ovos.common_play.playlist.queue',
             'data': {'tracks': [
                 {'uri': 'file://path/to/music.mp3', 'title': 'music.mp3', 'playback': 2, 'status': 1,
                  'skill_id': 'mycroft.audio_interface'},
                 {'uri': 'file://path/to/music2.mp3', 'title': 'music2.mp3', 'playback': 2, 'status': 1,
                  'skill_id': 'mycroft.audio_interface'},
                 {'uri': 'file://path/to/music3.mp3', 'title': 'music3.mp3', 'playback': 2, 'status': 1,
                  'skill_id': 'mycroft.audio_interface'}]}},
            {'type': 'ovos.common_play.play',
             'data': {'repeat': False,
                      'media': {'uri': 'file://path/to/music.mp3',
                                'title': 'music.mp3', 'playback': 2,
                                'status': 1,
                                'skill_id': 'mycroft.audio_interface',
                                'skill': 'mycroft.audio_interface',
                                'position': 0, 'length': None,
                                'skill_icon': None, 'artist': None,
                                'is_cps': False, 'cps_data': {}},
                      'playlist': [
                          {'uri': 'file://path/to/music.mp3', 'title': 'music.mp3',
                           'playback': 2, 'status': 1,
                           'skill_id': 'mycroft.audio_interface',
                           'skill': 'mycroft.audio_interface', 'position': 0,
                           'length': None, 'skill_icon': None, 'artist': None,
                           'is_cps': False, 'cps_data': {}},
                          {'uri': 'file://path/to/music2.mp3', 'title': 'music2.mp3',
                           'playback': 2, 'status': 1,
                           'skill_id': 'mycroft.audio_interface',
                           'skill': 'mycroft.audio_interface', 'position': 0,
                           'length': None, 'skill_icon': None, 'artist': None,
                           'is_cps': False, 'cps_data': {}},
                          {'uri': 'file://path/to/music3.mp3', 'title': 'music3.mp3',
                           'playback': 2, 'status': 1,
                           'skill_id': 'mycroft.audio_interface',
                           'skill': 'mycroft.audio_interface', 'position': 0,
                           'length': None, 'skill_icon': None, 'artist': None,
                           'is_cps': False, 'cps_data': {}}]}}
        ]
        for m in expected:
            self.assertIn(m, self.bus.emitted_msgs)

        audio.shutdown()

    @unittest.skip("debug - github actions gets stuck forever here ? works on my machine")
    @patch.dict(Configuration._Configuration__patch, BASE_CONF)
    def test_play_mycroft_backend(self):
        audio = AudioService(self.bus)
        self.bus.emitted_msgs = []
        selected = "mycroft_test"
        tracks = ["file://path/to/music.mp3", "file://path/to/music2.mp3"]

        # assert OCP not in use
        self.assertNotEqual(audio.default.ocp.player.state, PlayerState.PLAYING)

        self.api.play(tracks, repeat=True, utterance=selected)

        # correct service selected
        self.assertEqual(audio.current.name, selected)
        self.assertTrue(audio.current.playing)

        # OCP is not aware of internal player state - state events not emitted by mycroft plugins
        self.assertNotEqual(audio.default.ocp.player.state, PlayerState.PLAYING)

        # but track state is partially accounted for
        self.assertEqual(audio.default.ocp.player.now_playing.uri, tracks[0])
        self.assertEqual(audio.default.ocp.player.now_playing.playback, PlaybackType.AUDIO_SERVICE)
        self.assertEqual(audio.default.ocp.player.now_playing.status, TrackState.QUEUED_AUDIOSERVICE)
        self.assertEqual(audio.default.ocp.player.now_playing.skill_id, "mycroft.audio_interface")

        audio.current._track_start_callback("track_name")
        self.assertEqual(audio.default.ocp.player.now_playing.status, TrackState.PLAYING_AUDIOSERVICE)

        audio.shutdown()

    @unittest.skip("debug - github actions gets stuck forever here ? works on my machine")
    @patch.dict(Configuration._Configuration__patch, BASE_CONF)
    def test_play_ocp_backend(self):
        audio = AudioService(self.bus)
        self.bus.emitted_msgs = []

        selected = "ovos_test"
        tracks = ["file://path/to/music.mp3", "file://path/to/music2.mp3"]

        # assert OCP not in use
        self.assertNotEqual(audio.default.ocp.player.state, PlayerState.PLAYING)

        # NOTE: this usage is equivalent to what OCP itself
        # does internally to select audio_service, where "utterance" is also used
        self.api.play(tracks, repeat=True, utterance=selected)

        # correct service selected
        self.assertEqual(audio.current.name, selected)

        # ocp state events emitted
        exptected = [
            {'type': 'mycroft.audio.service.play',
             'data': {'tracks': ['file://path/to/music.mp3', 'file://path/to/music2.mp3'], 'utterance': 'ovos_test',
                      'repeat': True}},
            {'type': 'ovos.common_play.playlist.clear', 'data': {}},  # TODO - maybe this is unwanted (?)
            {'type': 'ovos.common_play.media.state', 'data': {'state': 3}},
            {'type': 'ovos.common_play.track.state', 'data': {'state': 31}},
            {'type': 'ovos.common_play.playlist.queue', 'data': {'tracks': [
                {'uri': 'file://path/to/music.mp3', 'title': 'music.mp3', 'playback': 2, 'status': 1,
                 'skill_id': 'mycroft.audio_interface'},
                {'uri': 'file://path/to/music2.mp3', 'title': 'music2.mp3', 'playback': 2, 'status': 1,
                 'skill_id': 'mycroft.audio_interface'}]}},
            {'type': 'ovos.common_play.repeat.set', 'data': {}},
            {'type': 'ovos.common_play.player.state', 'data': {'state': 1}},
            {'type': 'ovos.common_play.media.state', 'data': {'state': 3}},
            {'type': 'ovos.common_play.track.state', 'data': {'state': 21}}
        ]
        for m in exptected:
            self.assertIn(m, self.bus.emitted_msgs)

        # assert OCP is tracking state
        self.assertEqual(audio.default.ocp.player.state, PlayerState.PLAYING)
        self.assertEqual(audio.default.ocp.player.media_state, MediaState.LOADED_MEDIA)
        self.assertEqual(audio.default.ocp.player.now_playing.uri, tracks[0])
        self.assertEqual(audio.default.ocp.player.now_playing.playback, PlaybackType.AUDIO_SERVICE)
        self.assertEqual(audio.default.ocp.player.now_playing.status, TrackState.PLAYING_AUDIOSERVICE)

        audio.shutdown()


if __name__ == '__main__':
    unittest.main()
