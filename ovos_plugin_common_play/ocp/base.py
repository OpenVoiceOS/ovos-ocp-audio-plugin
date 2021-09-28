from ovos_utils.enclosure.api import EnclosureAPI


class OCPAbstractComponent:
    def __init__(self, player):
        """
        player: OCPInterface
        """
        self._player = player
        self.enclosure = EnclosureAPI(self.bus)

    @property
    def player(self):
        return self._player

    @property
    def settings(self):
        return self._player.settings

    @property
    def gui(self):
        return self._player.gui

    @property
    def bus(self):
        return self._player.bus
