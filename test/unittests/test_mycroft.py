import json
import unittest
from os.path import dirname
from mycroft.skills.intent_service import IntentService
from mycroft.skills.skill_loader import SkillLoader
from ovos_utils.messagebus import FakeBus

from ovos_plugin_common_play import OCPAudioBackend


class TestEnglishMediaIntents(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.bus = FakeBus()
        self.bus.emitted_msgs = []

        def get_msg(msg):
            self.bus.emitted_msgs.append(json.loads(msg))

        self.bus.on("message", get_msg)

    def test_auto_unload(self):
        intents = IntentService(self.bus)
        skill = SkillLoader(self.bus, f"{dirname(__file__)}/ovos_tskill_mycroft_cps")
        skill.skill_id = "skill-playback-control.mycroftai"
        skill.load()

        # assert that mycroft common play intents registered
        cps_msgs = [
            {'type': 'register_intent', 'data': {'name': 'skill-playback-control.mycroftai:play',
                                                 'requires': [['skill_playback_control_mycroftaiPlay',
                                                               'skill_playback_control_mycroftaiPlay'],
                                                              ['skill_playback_control_mycroftaiPhrase',
                                                               'skill_playback_control_mycroftaiPhrase']],
                                                 'at_least_one': [], 'optional': []},
             'context': {'skill_id': 'skill-playback-control.mycroftai'}},
            {'type': 'register_intent', 'data': {'name': 'skill-playback-control.mycroftai:handle_prev',
                                                 'requires': [['skill_playback_control_mycroftaiPrev',
                                                               'skill_playback_control_mycroftaiPrev'],
                                                              ['skill_playback_control_mycroftaiTrack',
                                                               'skill_playback_control_mycroftaiTrack']],
                                                 'at_least_one': [], 'optional': []},
             'context': {'skill_id': 'skill-playback-control.mycroftai'}},
            {'type': 'register_intent', 'data': {'name': 'skill-playback-control.mycroftai:handle_pause',
                                                 'requires': [['skill_playback_control_mycroftaiPause',
                                                               'skill_playback_control_mycroftaiPause']],
                                                 'at_least_one': [], 'optional': []},
             'context': {'skill_id': 'skill-playback-control.mycroftai'}},
            {'type': 'register_intent', 'data': {'name': 'skill-playback-control.mycroftai:handle_next',
                                                 'requires': [['skill_playback_control_mycroftaiNext',
                                                               'skill_playback_control_mycroftaiNext'],
                                                              ['skill_playback_control_mycroftaiTrack',
                                                               'skill_playback_control_mycroftaiTrack']],
                                                 'at_least_one': [], 'optional': []},
             'context': {'skill_id': 'skill-playback-control.mycroftai'}},
            {'type': 'register_intent',
             'data': {'name': 'skill-playback-control.mycroftai:handle_play', 'requires': [],
                      'at_least_one': [['skill_playback_control_mycroftaiPlayResume',
                                        'skill_playback_control_mycroftaiResume']], 'optional': []},
             'context': {'skill_id': 'skill-playback-control.mycroftai'}}
        ]
        for intent in cps_msgs:
            self.assertIn(intent, self.bus.emitted_msgs)

        # assert that mycroft common play intents loaded
        cps_intents = [
            {'name': 'skill-playback-control.mycroftai:handle_prev',
             'requires': [('skill_playback_control_mycroftaiPrev', 'skill_playback_control_mycroftaiPrev'),
                          ('skill_playback_control_mycroftaiTrack', 'skill_playback_control_mycroftaiTrack')],
             'at_least_one': [], 'optional': []},
            {'name': 'skill-playback-control.mycroftai:handle_play', 'requires': [],
             'at_least_one': [('skill_playback_control_mycroftaiPlayResume', 'skill_playback_control_mycroftaiResume')],
             'optional': []},
            {'name': 'skill-playback-control.mycroftai:handle_pause',
             'requires': [('skill_playback_control_mycroftaiPause', 'skill_playback_control_mycroftaiPause')],
             'at_least_one': [], 'optional': []},
            {'name': 'skill-playback-control.mycroftai:play',
             'requires': [('skill_playback_control_mycroftaiPlay', 'skill_playback_control_mycroftaiPlay'),
                          ('skill_playback_control_mycroftaiPhrase', 'skill_playback_control_mycroftaiPhrase')],
             'at_least_one': [], 'optional': []},
            {'name': 'skill-playback-control.mycroftai:handle_next',
             'requires': [('skill_playback_control_mycroftaiNext', 'skill_playback_control_mycroftaiNext'),
                          ('skill_playback_control_mycroftaiTrack', 'skill_playback_control_mycroftaiTrack')],
             'at_least_one': [], 'optional': []}
        ]
        for intent in cps_intents:
            self.assertIn(intent, intents.registered_intents)

        # load ocp
        self.bus.emitted_msgs = []
        cfg = {}
        ocp = OCPAudioBackend(cfg, self.bus)
        for idx, msg in enumerate(self.bus.emitted_msgs):
            if msg["data"].get("file_name"):
                self.bus.emitted_msgs[idx]["data"]["file_name"] = msg["data"]["file_name"].split("/")[-1]

        # assert that mycroft common play was deregistered
        disable_msgs = [
            {'type': 'skillmanager.deactivate', 'data': {'skill': 'skill-playback-control.mycroftai'}, 'context': {}},
            {'type': 'skillmanager.deactivate', 'data': {'skill': 'mycroft-playback-control.mycroftai'}, 'context': {}},
            {'type': 'skillmanager.deactivate', 'data': {'skill': 'mycroft-playback-control'}, 'context': {}},
            {'type': 'skillmanager.deactivate', 'data': {'skill': 'skill-playback-control'}, 'context': {}}
        ]  # possible skill-ids for mycroft skill
        for msg in disable_msgs:
            self.assertIn(msg, self.bus.emitted_msgs)
            # skill manager would call this if connected to bus
            if msg["data"]["skill"] == skill.skill_id:
                skill.deactivate()

        # assert that OCP intents registered
        ocp_msgs = [
            {'type': 'padatious:register_intent', 'data': {
                'file_name': 'play.intent',
                'name': 'ovos.common_play:play.intent', 'lang': 'en-us'}, 'context': {'skill_id': 'ovos.common_play'}},
            {'type': 'padatious:register_intent', 'data': {
                'file_name': 'read.intent',
                'name': 'ovos.common_play:read.intent', 'lang': 'en-us'}, 'context': {'skill_id': 'ovos.common_play'}},
            {'type': 'padatious:register_intent', 'data': {
                'file_name': 'open.intent',
                'name': 'ovos.common_play:open.intent', 'lang': 'en-us'}, 'context': {'skill_id': 'ovos.common_play'}},
            {'type': 'padatious:register_intent', 'data': {
                'file_name': 'next.intent',
                'name': 'ovos.common_play:next.intent', 'lang': 'en-us'}, 'context': {'skill_id': 'ovos.common_play'}},
            {'type': 'padatious:register_intent', 'data': {
                'file_name': 'prev.intent',
                'name': 'ovos.common_play:prev.intent', 'lang': 'en-us'}, 'context': {'skill_id': 'ovos.common_play'}},
            {'type': 'padatious:register_intent', 'data': {
                'file_name': 'pause.intent',
                'name': 'ovos.common_play:pause.intent', 'lang': 'en-us'}, 'context': {'skill_id': 'ovos.common_play'}},
            {'type': 'padatious:register_intent', 'data': {
                'file_name': 'resume.intent',
                'name': 'ovos.common_play:resume.intent', 'lang': 'en-us'}, 'context': {'skill_id': 'ovos.common_play'}},
            {'type': 'ovos.common_play.skills.get', 'data': {}, 'context': {}}
        ]
        for intent in ocp_msgs:
            self.assertIn(intent, self.bus.emitted_msgs)

        # assert that mycroft common play intents unloaded
        detach_msg = {'type': 'detach_skill',
                      'data': {'skill_id': 'skill-playback-control.mycroftai:'},
                      'context': {'skill_id': 'skill-playback-control.mycroftai'}}
        self.assertIn(detach_msg, self.bus.emitted_msgs)
        for intent in cps_intents:
            self.assertNotIn(intent, intents.registered_intents)


if __name__ == '__main__':
    unittest.main()
