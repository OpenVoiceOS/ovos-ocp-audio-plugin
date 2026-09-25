"""The GUI's EventSchedulerInterface comes from ovos_bus_client, not the
deprecated ``ovos_utils.events`` location."""
import unittest

from ovos_plugin_common_play.ocp import gui


class TestGuiEventScheduler(unittest.TestCase):
    def test_event_scheduler_interface_from_bus_client(self):
        self.assertTrue(
            gui.EventSchedulerInterface.__module__.startswith("ovos_bus_client"))


if __name__ == "__main__":
    unittest.main()
