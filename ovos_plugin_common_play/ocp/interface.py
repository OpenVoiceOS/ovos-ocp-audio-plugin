from ovos_workshop.ocp.player import OCPMediaPlayer
from ovos_workshop.ocp.settings import OCPSettings
from ovos_workshop.ocp.status import *
from ovos_utils.messagebus import get_mycroft_bus


class OCPInterface:
    """ interface for OVOS Common Playback Service """

    def __init__(self, bus=None, settings=None, audio_service=None):
        """
        Arguments:
            bus (MessageBus): mycroft messagebus connection
        """
        self.bus = bus or get_mycroft_bus()
        self.settings = settings or OCPSettings()
        self.player = OCPMediaPlayer(self.bus, self.settings,
                                     audio_service=audio_service)

    @property
    def player_state(self):
        return self.player.state

    def shutdown(self):
        self.stop()
        self.player.shutdown()

    # playback control
    def play(self):
        self.player.play()

    def play_media(self, track, disambiguation=None, playlist=None):
        self.player.play_media(track, disambiguation, playlist)

    def play_next(self):
        self.player.play_next()

    def play_prev(self):
        self.player.play_prev()

    def pause(self):
        self.player.pause()

    def resume(self):
        self.player.resume()

    def stop(self):
        stopped = False
        if self.player.state != PlayerState.STOPPED:
            stopped = True
        self.player.stop()
        return stopped

    def reset(self):
        self.player.reset()

    # searching
    def search(self, phrase, media_type=MediaType.GENERIC):
        return self.player.media.search(phrase, media_type)

    def search_skill(self, skill_id, phrase,
                     media_type=MediaType.GENERIC):
        return self.player.media.search_skill(skill_id, phrase, media_type)

    def clear_search(self):
        self.player.media.clear()


if __name__ == "__main__":
    from pprint import pprint

    cps = OCPInterface()

    # test lovecraft skills
    pprint(cps.search_skill("skill-omeleto", "movie",
                            MediaType.SHORT_FILM))

    exit()
    pprint(cps.search("the thing in the doorstep"))

    pprint(cps.search("dagon", MediaType.VIDEO))

    pprint(cps.search("dagon hp lovecraft"))
