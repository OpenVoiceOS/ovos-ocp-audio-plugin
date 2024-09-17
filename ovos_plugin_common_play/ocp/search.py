import time
from threading import RLock

from ovos_bus_client.message import Message
from ovos_utils.log import LOG
from ovos_workshop.decorators.ocp import MediaType

from ovos_plugin_common_play.ocp.base import OCPAbstractComponent
from ovos_plugin_common_play.ocp.media import Playlist


class OCPSearch(OCPAbstractComponent):
    def __init__(self, player=None):  # OCPMediaPlayer
        super(OCPSearch, self).__init__(player)
        self.search_playlist = Playlist()
        self.ocp_skills = {}
        self.featured_skills = {}
        self.search_lock = RLock()
        if player:
            self.bind(player)

    def bind(self, player):  # OCPMediaPlayer
        self._player = player
        self.add_event("ovos.common_play.skills.detach",
                       self.handle_ocp_skill_detach)
        self.add_event("ovos.common_play.announce",
                       self.handle_skill_announce)
        self.add_event("ovos.common_play.search.start",
                       self.handle_search_start)

    def handle_search_start(self, message):
        self.gui.notify_search_status("Searching...")

    def shutdown(self):
        self.remove_event("ovos.common_play.announce")
        self.remove_event("ovos.common_play.skills.detach")

    def handle_skill_announce(self, message):
        skill_id = message.data.get("skill_id")
        skill_name = message.data.get("skill_name") or skill_id
        img = message.data.get("thumbnail")
        has_featured = bool(message.data.get("featured_tracks"))
        media_type = message.data.get("media_type") or [MediaType.GENERIC]

        if skill_id not in self.ocp_skills:
            LOG.debug(f"Registered {skill_id}")
            self.ocp_skills[skill_id] = []

        if has_featured:
            LOG.debug(f"Found skill with featured media: {skill_id}")
            self.featured_skills[skill_id] = {
                "skill_id": skill_id,
                "skill_name": skill_name,
                "thumbnail": img,
                "media_type": media_type
            }

    def handle_ocp_skill_detach(self, message):
        skill_id = message.data["skill_id"]
        if skill_id in self.ocp_skills:
            self.ocp_skills.pop(skill_id)
        if skill_id in self.featured_skills:
            self.featured_skills.pop(skill_id)

    def get_featured_skills(self, adult=False):
        # trigger a presence announcement from all loaded ocp skills
        self.bus.emit(Message("ovos.common_play.skills.get"))
        time.sleep(0.2)
        skills = list(self.featured_skills.values())
        if adult:
            return skills
        return [s for s in skills
                if MediaType.ADULT not in s["media_type"] and
                MediaType.HENTAI not in s["media_type"]]
