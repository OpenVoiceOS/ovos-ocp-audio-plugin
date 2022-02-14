import os
import sys
import unittest
from os.path import join, dirname, isfile

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from padacioso import IntentContainer


class TestEnglishMediaIntents(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.media_intents = IntentContainer()

        locale_folder = join(dirname(dirname(__file__)),
                             "ovos_plugin_common_play", "ocp", "res",
                             "locale", "en-us")
        for intent_name in ["music", "video", "audiobook", "radio",
                            "radio_drama", "game", "tv",
                            "podcast", "news", "movie", "short_movie",
                            "silent_movie", "bw_movie",
                            "documentaries", "comic", "movietrailer",
                            "behind_scenes", "porn"]:
            path = join(locale_folder, intent_name + ".intent")
            if not isfile(path):
                continue
            with open(path) as intent:
                samples = intent.read().split("\n")
                for idx, s in enumerate(samples):
                    samples[idx] = s.replace("{{", "{").replace("}}", "}")
            self.media_intents.add_intent(intent_name, samples)

    def test_generic(self):
        utts = ["play",
                "play something"]
        for utt in utts:
            self.assertEqual(self.media_intents.calc_intent(utt),
                             {'name': None, 'entities': {}})

    def test_radio(self):
        self.assertEqual(
            self.media_intents.calc_intent("play heavy metal radio"),
            {'conf': 0.9, 'entities': {'query': 'heavy metal'}, 'name': 'radio'})
        self.assertEqual(
            self.media_intents.calc_intent("play radio"),
            {'conf': 1, 'entities': {}, 'name': 'radio'})
        self.assertEqual(
            self.media_intents.calc_intent("play internet radio"),
            {'conf': 1, 'entities': {}, 'name': 'radio'})

    def test_music(self):
        self.assertEqual(
            self.media_intents.calc_intent("play heavy metal music"),
            {'conf': 0.9, 'entities': {'query': 'heavy metal'}, 'name': 'music'})
        self.assertEqual(
            self.media_intents.calc_intent("play music"),
            {'conf': 1, 'entities': {}, 'name': 'music'})
        self.assertEqual(
            self.media_intents.calc_intent("play some music"),
            {'conf': 0.9, 'entities': {'query': 'some'}, 'name': 'music'})

    def test_movie(self):
        self.assertEqual(
            self.media_intents.calc_intent("play a horror film"),
            {'conf': 0.9, 'entities': {'query': 'horror'}, 'name': 'movie'})
        self.assertEqual(
            self.media_intents.calc_intent("play a movie"),
            {'conf': 0.9, 'entities': {'query': 'a'}, 'name': 'movie'})
        self.assertEqual(
            self.media_intents.calc_intent("play the matrix movie"),
            {'conf': 0.9, 'entities': {'query': 'the matrix'}, 'name': 'movie'})


if __name__ == '__main__':
    unittest.main()
