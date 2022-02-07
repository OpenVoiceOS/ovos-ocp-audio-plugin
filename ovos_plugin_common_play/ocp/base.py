from ovos_plugin_common_play.ocp.settings import OCPSettings


class OCPAbstractComponent:
    def __init__(self, player=None):
        """
        player: OCPInterface
        """
        self._player = None
        if player:
            self.bind(player)

    def bind(self, player):
        self._player = player

    @property
    def player(self):
        return self._player

    @property
    def settings(self):
        if not self._player:
            return OCPSettings()
        return self._player.settings

    @property
    def enclosure(self):
        if not self._player:
            return None
        return self._player.enclosure

    @property
    def gui(self):
        if not self._player:
            return None
        return self._player.gui

    @property
    def bus(self):
        if not self._player:
            return None
        return self._player.bus

    def add_event(self, msg_type, handler):
        self.player.add_event(msg_type, handler)

    def remove_event(self, msg_type):
        self.player.remove_event(msg_type)
