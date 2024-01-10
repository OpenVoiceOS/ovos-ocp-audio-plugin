from ovos_plugin_manager.templates.audio import AudioBackend


class TestMycroftAudioService(AudioBackend):
    def __init__(self, config, bus, name='mycroft_test'):
        super().__init__(config, bus)
        self.config = config
        self.bus = bus
        self.name = name
        self.index = 0
        self.tracks = []
        self.stopped = True
        self.paused = False
        self.playing = False
        self.ducked = False

    def supported_uris(self):
        return ['file', 'http']

    def clear_list(self):
        self.tracks = []

    def add_list(self, tracks):
        self.tracks += tracks

    def play(self, repeat=False):
        self.index = 0
        self.playing = True

    def stop(self):
        self.stopped = True
        self.playing = False
        return self.stopped

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def next(self):
        # Terminate process to continue to next
        self.index += 1

    def previous(self):
        self.index -= 1

    def lower_volume(self):
        self.ducked = True

    def restore_volume(self):
        self.ducked = False


def load_service(base_config, bus):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'mycroft_test' and
                backends[b].get('active', False)]
    instances = [TestMycroftAudioService(s[1], bus, s[0]) for s in services]
    return instances
