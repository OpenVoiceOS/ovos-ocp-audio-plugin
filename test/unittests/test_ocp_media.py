import unittest
from unittest.mock import Mock

from ovos_bus_client import Message

from ovos_plugin_common_play.ocp.media import MediaEntry, Playlist, NowPlaying
from ovos_plugin_common_play.ocp.status import MediaType, PlaybackType, TrackState, MediaState
from ovos_utils.messagebus import FakeBus


valid_search_results = [
    {'media_type': MediaType.MUSIC,
     'playback': PlaybackType.AUDIO,
     'image': 'https://freemusicarchive.org/legacy/fma-smaller.jpg',
     'skill_icon': 'https://freemusicarchive.org/legacy/fma-smaller.jpg',
     'uri': 'https://freemusicarchive.org/track/07_-_Quantum_Jazz_-_Orbiting_A_Distant_Planet/stream/',
     'title': 'Orbiting A Distant Planet',
     'artist': 'Quantum Jazz',
     'skill_id': 'skill-free_music_archive.neongeckocom',
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


class TestMediaEntry(unittest.TestCase):
    def test_init(self):
        data = valid_search_results[0]

        # Test MediaEntry init
        entry = MediaEntry(**data)
        self.assertEqual(entry.title, data['title'])
        self.assertEqual(entry.uri, data['uri'])
        self.assertEqual(entry.artist, data['artist'])
        self.assertEqual(entry.skill_id, data['skill_id'])
        self.assertEqual(entry.status, TrackState.DISAMBIGUATION)
        self.assertEqual(entry.playback, data['playback'])
        self.assertEqual(entry.image, data['image'])
        self.assertEqual(entry.position, 0)
        self.assertIsNone(entry.phrase)
        self.assertIsNone(entry.length)
        self.assertEqual(entry.skill_icon, data['skill_icon'])
        self.assertIsInstance(entry.bg_image, str)
        self.assertFalse(entry.is_cps)
        self.assertEqual(entry.data, {"media_type": data['media_type']})
        self.assertEqual(entry.cps_data, dict())
        self.assertEqual(entry.javascript, "")

        # Test playback passed as int
        data['playback'] = int(data['playback'])
        new_entry = MediaEntry(**data)
        self.assertEqual(entry, new_entry)

        # TODO: Test file URI
        # TODO: Test defined length
        # TODO: Test defined background image
        # TODO: Test defined cps_data
        # TODO: Test defined javascript

    def test_update(self):
        # TODO
        pass

    def test_from_dict(self):
        dict_data = valid_search_results[1]
        from_dict = MediaEntry.from_dict(dict_data)
        self.assertIsInstance(from_dict, MediaEntry)
        from_init = MediaEntry(dict_data["title"], dict_data["uri"],
                               image=dict_data["image"],
                               match_confidence=dict_data["match_confidence"],
                               playback=PlaybackType.AUDIO,
                               skill_icon=dict_data["skill_icon"],
                               artist=dict_data["artist"])
        self.assertEqual(from_init, from_dict)

        # Test int playback
        dict_data['playback'] = int(dict_data['playback'])
        new_entry = MediaEntry.from_dict(dict_data)
        self.assertEqual(from_dict, new_entry)

        self.assertIsInstance(MediaEntry.from_dict({}), MediaEntry)

    def test_info(self):
        # TODO
        pass

    def test_infocard(self):
        # TODO
        pass

    def test_mpris_metadata(self):
        # TODO
        pass

    def test_as_dict(self):
        # TODO
        pass

    def test_mimetype(self):
        # TODO
        pass


class TestPlaylist(unittest.TestCase):
    def test_properties(self):
        # Empty Playlist
        pl = Playlist()
        self.assertEqual(pl.position, 0)
        self.assertEqual(pl.entries, [])
        self.assertIsNone(pl.current_track)
        self.assertTrue(pl.is_first_track)
        self.assertTrue(pl.is_last_track)

        # Playlist of dicts
        pl = Playlist(valid_search_results)
        self.assertEqual(pl.position, 0)
        self.assertEqual(len(pl.entries), len(valid_search_results))
        for entry in pl.entries:
            self.assertIsInstance(entry, MediaEntry)
        self.assertIsInstance(pl.current_track, MediaEntry)
        self.assertTrue(pl.is_first_track)
        self.assertFalse(pl.is_last_track)

    def test_goto_start(self):
        # TODO
        pass

    def test_clear(self):
        # TODO
        pass

    def test_sort_by_conf(self):
        # TODO
        pass

    def test_add_entry(self):
        # TODO
        pass

    def test_remove_entry(self):
        # TODO
        pass

    def test_replace(self):
        # TODO
        pass

    def test_set_position(self):
        # TODO
        pass

    def test_goto_track(self):
        # TODO
        pass

    def test_next_track(self):
        # TODO
        pass

    def test_prev_track(self):
        # TODO
        pass

    def test_validate_position(self):
        # Test empty playlist
        pl = Playlist()
        pl._position = 0
        pl._validate_position()
        self.assertEqual(pl.position, 0)
        pl._position = -1
        pl._validate_position()
        self.assertEqual(pl.position, 0)
        pl._position = 1
        pl._validate_position()
        self.assertEqual(pl.position, 0)

        # Test playlist of len 1
        pl = Playlist([valid_search_results[0]])
        pl._position = 0
        pl._validate_position()
        self.assertEqual(pl.position, 0)
        pl._position = 1
        pl._validate_position()
        self.assertEqual(pl.position, 0)

        # Test playlist of len>1
        pl = Playlist(valid_search_results)
        pl._position = 0
        pl._validate_position()
        self.assertEqual(pl.position, 0)
        pl._position = 1
        pl._validate_position()
        self.assertEqual(pl.position, 1)
        pl._position = 10
        pl._validate_position()
        self.assertEqual(pl.position, 0)


class TestNowPlaying(unittest.TestCase):
    from ovos_plugin_common_play.ocp import OCPMediaPlayer

    bus = FakeBus()
    ocp = OCPMediaPlayer(bus)
    player = ocp.now_playing

    def test_init_bind_shutdown(self):
        now_playing = NowPlaying()
        self.assertIsInstance(now_playing, NowPlaying)
        self.assertIsInstance(now_playing, MediaEntry)

        # Bind OCP
        now_playing.bind(self.ocp)
        self.assertEqual(now_playing._player, self.ocp)
        self.assertEqual(now_playing.bus, self.bus)
        self.assertEqual(now_playing._settings, self.ocp.settings)


        # TODO: Improve tests for event registration
        events = [
            "ovos.common_play.track.state",
            "ovos.common_play.playback_time",
            "gui.player.media.service.get.meta",
            "mycroft.audio.service.track_info_reply",
        ]
        media_events = [
            "ovos.common_play.media.state",
            "ovos.common_play.play",
            "mycroft.audio.service.play",
            "mycroft.audio.playing_track"
        ]
        # Check event registration
        for event in media_events:
            self.assertGreaterEqual(len(self.bus.ee.listeners(event)), 1)
        for event in events:
            self.assertGreaterEqual(len(self.bus.ee.listeners(event)), 1)

        # Check shutdown
        now_playing.shutdown()
        for event in events:
            self.assertLessEqual(len(self.bus.ee.listeners(event)), 2)

    def test_as_entry(self):
        entry = MediaEntry.from_dict(valid_search_results[0])
        player = NowPlaying()
        player.update(entry)
        self.assertNotIsInstance(player.as_entry(), NowPlaying)
        self.assertIsInstance(player.as_entry(), MediaEntry)
        self.assertEqual(player.as_entry(), entry)

    def test_reset(self):
        entry = MediaEntry.from_dict(valid_search_results[0])
        self.player.update(entry)
        self.assertEqual(self.player.as_entry(), entry)

        self.assertNotEqual(self.player.title, "")
        self.assertNotEqual(self.player.artist, None)
        self.assertNotEqual(self.player.skill_icon, None)
        self.assertNotEqual(self.player.skill_id, None)
        # self.assertNotEqual(self.player.position, 0)
        # self.assertNotEqual(self.player.length, None)
        # self.assertNotEqual(self.player.is_cps, False)
        # self.assertNotEqual(self.player.cps_data, dict())
        self.assertNotEqual(self.player.data, dict())
        # self.assertNotEqual(self.player.phrase, None)
        # self.assertNotEqual(self.player.javascript, "")
        self.assertNotEqual(self.player.playback, PlaybackType.UNDEFINED)
        # self.assertNotEqual(self.player.status, TrackState.DISAMBIGUATION)

        self.player.reset()
        self.assertEqual(self.player.title, "")
        self.assertEqual(self.player.artist, None)
        self.assertEqual(self.player.skill_icon, None)
        self.assertEqual(self.player.skill_id, None)
        self.assertEqual(self.player.position, 0)
        self.assertEqual(self.player.length, None)
        self.assertEqual(self.player.is_cps, False)
        self.assertEqual(self.player.cps_data, dict())
        self.assertEqual(self.player.data, dict())
        self.assertEqual(self.player.phrase, None)
        self.assertEqual(self.player.javascript, "")
        self.assertEqual(self.player.playback, PlaybackType.UNDEFINED)
        self.assertEqual(self.player.status, TrackState.DISAMBIGUATION)

    def test_update(self):
        # TODO
        pass

    def test_extract_stream(self):
        # TODO
        pass

    def test_handle_external_play(self):
        # TODO
        pass

    def test_handle_player_metadata_request(self):
        # TODO
        pass

    def test_handle_track_state_change(self):
        self.player.status = TrackState.DISAMBIGUATION

        # Test invalid update
        with self.assertRaises(ValueError):
            self.player.handle_track_state_change(
                Message("", {"state": "PLAYING_AUDIO"}))
        with self.assertRaises(ValueError):
            self.player.handle_track_state_change(
                Message("", {"stat": "PLAYING_AUDIO"}))

        # Test int update
        self.player.handle_track_state_change(
            Message("", {"state": int(TrackState.PLAYING_AUDIO)}))
        self.assertEqual(self.player.status, TrackState.PLAYING_AUDIO)

        # Test TrackState update
        self.player.handle_track_state_change(
            Message("", {"state": TrackState.PLAYING_SKILL}))
        self.assertEqual(self.player.status, TrackState.PLAYING_SKILL)

    def test_handle_media_state_change(self):
        real_reset = self.player.reset
        self.player.reset = Mock()

        # Test invalid update
        with self.assertRaises(ValueError):
            self.player.handle_media_state_change(
                Message("", {"state": "END_OF_MEDIA"}))
        with self.assertRaises(ValueError):
            self.player.handle_media_state_change(
                Message("", {"stat": "END_OF_MEDIA"}))

        # Test int update
        self.player.handle_media_state_change(
            Message("", {"state": int(MediaState.NO_MEDIA)}))

        # Test MediaState update
        self.player.handle_media_state_change(
            Message("", {"state": MediaState.BUFFERED_MEDIA}))

        # Test END_OF_MEDIA
        self.player.handle_media_state_change(
            Message("", {"state": MediaState.END_OF_MEDIA}))

        self.player.reset.assert_not_called()
        self.player.reset = real_reset

    def test_handle_sync_seekbar(self):
        # TODO
        pass

    def test_handle_sync_trackinfo(self):
        # TODO
        pass

    def test_handle_audio_service_play(self):
        # TODO
        pass

    def test_handle_audio_service_play_start(self):
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
