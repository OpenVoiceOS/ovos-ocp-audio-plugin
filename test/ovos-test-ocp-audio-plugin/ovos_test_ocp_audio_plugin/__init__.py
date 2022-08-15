from ovos_plugin_common_play.ocp.base import OCPAudioPlayerBackend


class OVOSTestAudioService(OCPAudioPlayerBackend):
    def __init__(self, config, bus=None, name='ovos_test'):
        super(OVOSTestAudioService, self).__init__(config, bus)
        self.name = name

    def supported_uris(self):
        uris = ['file', 'http']
        return uris

    def play(self, repeat=False):
        """ Play playlist using simple. """
        self.ocp_start()

    def stop(self):
        """ Stop simple playback. """
        if self._now_playing:
            self.ocp_stop()
            return True
        return False

    def pause(self):
        """ Pause simple playback. """
        if self._now_playing:
            self.ocp_pause()

    def resume(self):
        """ Resume paused playback. """
        if self._now_playing:
            self.ocp_resume()


def load_service(base_config, bus):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'ovos_test' and
                backends[b].get('active', False)]

    instances = [OVOSTestAudioService(s[1], bus, s[0]) for s in services]
    return instances
