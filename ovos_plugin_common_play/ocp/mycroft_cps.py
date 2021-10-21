import random
import time

from ovos_plugin_common_play.ocp.base import OCPAbstractComponent
from ovos_plugin_common_play.ocp.status import *
from ovos_utils.messagebus import Message, wait_for_reply


class MycroftCommonPlayInterface(OCPAbstractComponent):
    """ interface for mycroft common play """

    def __init__(self, player=None):
        super().__init__(player)
        self.query_replies = {}
        self.query_extensions = {}
        self.waiting = False
        self.start_ts = 0
        if player:
            self.bind(player)

    def bind(self, player):
        self._player = player
        self.add_event("play:query.response",
                       self.handle_cps_response)

    @property
    def cps_status(self):
        return wait_for_reply('play:status.query',
                              reply_type="play:status.response",
                              bus=self.bus).data

    def handle_cps_response(self, message):
        search_phrase = message.data["phrase"]

        if ("searching" in message.data and
                search_phrase in self.query_extensions):
            # Manage requests for time to complete searches
            skill_id = message.data["skill_id"]
            if message.data["searching"]:
                # extend the timeout by N seconds
                # IGNORED HERE, used in mycroft-playback-control skill
                if skill_id not in self.query_extensions[search_phrase]:
                    self.query_extensions[search_phrase].append(skill_id)
            else:
                # Search complete, don't wait on this skill any longer
                if skill_id in self.query_extensions[search_phrase]:
                    self.query_extensions[search_phrase].remove(skill_id)

        elif search_phrase in self.query_replies:
            # Collect all replies until the timeout
            self.query_replies[message.data["phrase"]].append(message.data)

            # forward response in OCP format
            data = self.cps2ocp(message.data)
            self.bus.emit(message.forward(
                "ovos.common_play.query.response", data))

    def send_query(self, phrase, media_type=MediaType.GENERIC):
        self.query_replies[phrase] = []
        self.query_extensions[phrase] = []
        self.bus.emit(Message('play:query', {"phrase": phrase,
                                             "question_type": media_type}))

    def get_results(self, phrase):
        if self.query_replies.get(phrase):
            return self.query_replies[phrase]
        return []

    def search(self, phrase, media_type=MediaType.GENERIC,
               timeout=5):
        self.send_query(phrase, media_type)
        self.waiting = True
        start_ts = time.time()
        while self.waiting and time.time() - start_ts <= timeout:
            time.sleep(0.2)
        self.waiting = False
        return self.get_results(phrase)

    @staticmethod
    def cps2ocp(res, media_type=MediaType.GENERIC):
        data = {
            "playback": PlaybackType.SKILL,
            "media_type": media_type,
            "is_cps": True,
            "cps_data":  res['callback_data'],
            "skill_id": res["skill_id"],
            "phrase": res["phrase"],
            'match_confidence': res["conf"] * 100,
            "title": res["phrase"],
            "artist": res["skill_id"]
        }
        return {'phrase': res["phrase"],
                "is_old_style": True,
                'results': [data],
                'searching': False,
                'skill_id': res["skill_id"]}
