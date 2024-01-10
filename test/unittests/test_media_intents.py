import os
import sys
import unittest
from os.path import join, dirname, isfile

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import ovos_plugin_common_play
from padacioso import IntentContainer


class TestEnglishMediaIntents(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.media_intents = IntentContainer()

        locale_folder = join(dirname(ovos_plugin_common_play.__file__),
                             "ocp", "res", "locale", "en-us")
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
        intent = self.media_intents.calc_intent("play heavy metal radio")
        self.assertEqual(intent['name'], 'radio')
        self.assertEqual(intent['entities'], {'query': 'heavy metal'})
        self.assertGreaterEqual(intent['conf'], 0.9)

        self.assertEqual(
            self.media_intents.calc_intent("play radio"),
            {'conf': 1, 'entities': {}, 'name': 'radio'})

        self.assertEqual(
            self.media_intents.calc_intent("play internet radio"),
            {'conf': 1, 'entities': {}, 'name': 'radio'})

    def test_music(self):
        intent = self.media_intents.calc_intent("play heavy metal music")
        self.assertEqual(intent['name'], 'music')
        self.assertEqual(intent['entities'], {'query': 'heavy metal'})
        self.assertGreaterEqual(intent['conf'], 0.9)

        self.assertEqual(
            self.media_intents.calc_intent("play music"),
            {'conf': 1, 'entities': {}, 'name': 'music'})

        intent = self.media_intents.calc_intent("play some music")
        self.assertEqual(intent['name'], 'music')
        self.assertEqual(intent['entities'], {'query': 'some'})
        self.assertGreaterEqual(intent['conf'], 0.9)

    def test_movie(self):
        intent = self.media_intents.calc_intent("play a horror film")
        self.assertEqual(intent['name'], 'movie')
        self.assertEqual(intent['entities'], {'query': 'horror'})
        self.assertGreaterEqual(intent['conf'], 0.9)

        intent = self.media_intents.calc_intent("play a movie")
        self.assertEqual(intent['name'], 'movie')
        self.assertEqual(intent['entities'], {'query': 'a'})
        self.assertGreaterEqual(intent['conf'], 0.9)

        intent = self.media_intents.calc_intent("play the matrix movie")
        self.assertEqual(intent['name'], 'movie')
        self.assertEqual(intent['entities'], {'query': 'the matrix'})
        self.assertGreaterEqual(intent['conf'], 0.9)


if __name__ == '__main__':
    unittest.main()
