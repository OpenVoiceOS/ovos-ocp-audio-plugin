import unittest


class TestUtils(unittest.TestCase):
    def test_plugins_init(self):
        from ovos_plugin_common_play.ocp.utils import ocp_plugins
        from ovos_plugin_manager.ocp import StreamHandler
        self.assertIsInstance(ocp_plugins, StreamHandler)

    def test_available_extractors(self):
        from ovos_plugin_common_play.ocp.utils import available_extractors
        extractors = available_extractors()
        self.assertIsInstance(extractors, list)
        for ex in extractors:
            self.assertIsInstance(ex, str)
