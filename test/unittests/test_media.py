import unittest

from ovos_plugin_common_play.ocp.media import MediaEntry, Playlist
from ovos_plugin_common_play.ocp.status import MediaType, PlaybackType


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


class TestMediaEntry(unittest.TestCase):
    def test_update(self):
        # TODO
        pass

    def test_from_dict(self):
        dict_data = valid_search_results[0]
        from_dict = MediaEntry.from_dict(dict_data)
        self.assertIsInstance(from_dict, MediaEntry)
        from_init = MediaEntry(dict_data["title"], dict_data["uri"],
                               image=dict_data["image"],
                               match_confidence=dict_data["match_confidence"],
                               playback=PlaybackType.AUDIO,
                               skill_icon=dict_data["skill_icon"],
                               artist=dict_data["artist"])
        self.assertEqual(from_init, from_dict)

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
    def test(self):
        pass


if __name__ == "__main__":
    unittest.main()
