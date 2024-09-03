import unittest


class TestUtils(unittest.TestCase):

    def test_available_extractors(self):
        from ovos_plugin_manager.ocp import available_extractors
        extractors = available_extractors()
        self.assertIsInstance(extractors, list)
        for ex in extractors:
            self.assertIsInstance(ex, str)
