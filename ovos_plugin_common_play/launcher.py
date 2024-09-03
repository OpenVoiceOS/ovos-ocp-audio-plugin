#!/usr/bin/env python3
from ovos_bus_client import MessageBusClient
from ovos_utils import wait_for_exit_signal

from ovos_plugin_common_play.ocp import OCP
from ovos_plugin_common_play.ocp.constants import OCP_ID


def main():
    """
    Console script entrypoint
    USAGE: ovos-ocp-standalone
    """
    bus = MessageBusClient()
    bus.run_in_thread()
    bus.connected_event.wait()
    config = {"mode": "external"}

    try:
        ocp = OCP(bus=bus, skill_id=OCP_ID, settings=config)
    except ImportError:
        print("OCP is not available")
        ocp = None

    wait_for_exit_signal()

    if ocp:
        ocp.shutdown()


if __name__ == "__main__":
    main()
