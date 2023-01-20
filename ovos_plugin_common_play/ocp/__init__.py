from os.path import join, dirname, isfile

from ovos_plugin_common_play.ocp.constants import OCP_ID
from ovos_workshop.decorators.ocp import *
from ovos_plugin_common_play.ocp.gui import OCPMediaPlayerGUI
from ovos_plugin_common_play.ocp.player import OCPMediaPlayer
from ovos_plugin_common_play.ocp.status import *
from ovos_utils.gui import can_use_gui
from ovos_utils.log import LOG
from ovos_plugin_common_play.ocp.utils import create_desktop_file
from ovos_utils.messagebus import Message
from ovos_workshop import OVOSAbstractApplication
from padacioso import IntentContainer
from ovos_utils.intents.intent_service_interface import IntentQueryApi
from threading import Event, Lock


class OCP(OVOSAbstractApplication):
    intent2media = {
        "music": MediaType.MUSIC,
        "video": MediaType.VIDEO,
        "audiobook": MediaType.AUDIOBOOK,
        "radio": MediaType.RADIO,
        "radio_drama": MediaType.RADIO_THEATRE,
        "game": MediaType.GAME,
        "tv": MediaType.TV,
        "podcast": MediaType.PODCAST,
        "news": MediaType.NEWS,
        "movie": MediaType.MOVIE,
        "short_movie": MediaType.SHORT_FILM,
        "silent_movie": MediaType.SILENT_MOVIE,
        "bw_movie": MediaType.BLACK_WHITE_MOVIE,
        "documentaries": MediaType.DOCUMENTARY,
        "comic": MediaType.VISUAL_STORY,
        "movietrailer": MediaType.TRAILER,
        "behind_scenes": MediaType.BEHIND_THE_SCENES,

    }
    # filtered content
    adultintents = {
        "porn": MediaType.ADULT,
        "hentai": MediaType.HENTAI
    }

    def __init__(self, bus=None, lang=None, settings=None):
        # settings = settings or OCPSettings()
        res_dir = join(dirname(__file__), "res")
        gui = OCPMediaPlayerGUI()
        super().__init__(skill_id=OCP_ID, resources_dir=res_dir,
                         bus=bus, lang=lang, gui=gui)
        if settings:
            LOG.debug(f"Updating settings from value passed at init")
            self.settings.merge(settings)
        self._intents_event = Event()
        self._intent_registration_lock = Lock()
        self.player = OCPMediaPlayer(bus=self.bus,
                                     lang=self.lang,
                                     settings=self.settings,
                                     resources_dir=res_dir,
                                     gui=self.gui)
        self.media_intents = IntentContainer()
        self.register_ocp_api_events()
        self.register_media_intents()

        self.add_event("mycroft.ready", self.replace_mycroft_cps, once=True)
        skills_ready = self.bus.wait_for_response(
            Message("mycroft.skills.is_ready",
                    context={"source": [self.skill_id],
                             "destination": ["skills"]}))
        if skills_ready and skills_ready.data.get("status"):
            self.remove_event("mycroft.ready")
            self.replace_mycroft_cps(skills_ready)
        try:
            create_desktop_file()
        except:  # permission errors and stuff
            pass

    def handle_ping(self, message):
        self.bus.emit(message.reply("ovos.common_play.pong"))

    def register_ocp_api_events(self):
        self.add_event("ovos.common_play.ping", self.handle_ping)
        self.add_event('ovos.common_play.home', self.handle_home)
        # bus api shared with intents
        self.add_event("ovos.common_play.search", self.handle_play)

    def handle_home(self):
        # homescreen / launch from .desktop
        self.gui.show_home(app_mode=True)

    def register_ocp_intents(self, message=None):
        with self._intent_registration_lock:
            if not self._intents_event.is_set():
                missing = True
                LOG.debug("Intents register event not set")
            else:
                # check list of registered intents
                # if needed register ocp intents again
                # this accounts for restarts etc
                i = IntentQueryApi(self.bus)
                intents = i.get_padatious_manifest()
                missing = not any((e.startswith(f"{self.skill_id}:")
                                  for e in intents))
                LOG.debug(f'missing={missing} | {intents}')

            if missing:
                LOG.info(f"OCP intents missing, registering for {self}")
                self.register_intent("play.intent", self.handle_play)
                self.register_intent("read.intent", self.handle_read)
                self.register_intent("open.intent", self.handle_open)
                self.register_intent("next.intent", self.handle_next)
                self.register_intent("prev.intent", self.handle_prev)
                self.register_intent("pause.intent", self.handle_pause)
                self.register_intent("resume.intent", self.handle_resume)
                self._intents_event.set()

            # trigger a presence announcement from all loaded ocp skills
            self.bus.emit(Message("ovos.common_play.skills.get"))

    def register_media_intents(self):
        """
        NOTE: uses the same format as mycroft .intent files, language
        support is handled the same way
        """
        locale_folder = join(dirname(__file__), "res", "locale", self.lang)
        intents = self.intent2media
        if self.settings.get("adult_content", False):
            intents.update(self.adultintents)

        for intent_name in intents:
            path = join(locale_folder, intent_name + ".intent")
            if not isfile(path):
                continue
            with open(path) as intent:
                samples = intent.read().split("\n")
                for idx, s in enumerate(samples):
                    samples[idx] = s.replace("{{", "{").replace("}}", "}")
            LOG.debug(f"registering media type intent: {intent_name}")
            self.media_intents.add_intent(intent_name, samples)

    def replace_mycroft_cps(self, message=None):
        """
        Deactivates any Mycroft playback-control skills and ensures OCP intents
        are registered. Registers a listener so this method is called any time
        `mycroft.ready` is emitted.
        @param message: `mycroft.ready` message triggering this check
        """
        mycroft_cps_ids = [
            # disable mycroft cps, ocp replaces it and intents conflict
            "skill-playback-control.mycroftai",  # the convention
            "mycroft-playback-control.mycroftai",  # msm install
            # (mycroft skills override the repo name ???? )
            "mycroft-playback-control",
            "skill-playback-control"  # simple git clone
        ]

        # disable any loaded mycroft cps skill
        for skill_id in mycroft_cps_ids:
            self.bus.emit(Message('skillmanager.deactivate',
                                  {"skill": skill_id}))
        # register OCP own intents
        self.register_ocp_intents()

        # whenever we detect a skill loading, if its mycroft cps disable it!
        def unload_mycroft_cps(message):
            skill_id = message.data["id"]
            if skill_id in mycroft_cps_ids:
                self.bus.emit(Message('skillmanager.deactivate',
                                      {"skill": skill_id}))

        if ("mycroft.skills.loaded", unload_mycroft_cps) not in self.events:
            self.add_event("mycroft.skills.loaded", unload_mycroft_cps)

        # if skills service (re)loads (re)register OCP
        if ("mycroft.ready", self.replace_mycroft_cps) in self.events:
            LOG.warning("Method already registered!")
        self.add_event("mycroft.ready",  self.replace_mycroft_cps, once=True)

    def default_shutdown(self):
        self.player.shutdown()

    def classify_media(self, query):
        """ this method uses a strict regex based parser to determine what
        media type is being requested, this helps in the media process
        - only skills that support media type are considered
        - if no matches a generic media is performed
        - some skills only answer for specific media types, usually to avoid over matching
        - skills may use media type to calc confidence
        - skills may ignore media type

        NOTE: uses the same format as mycroft .intent files, language
        support is handled the same way
        """
        if self.voc_match(query, "audio_only"):
            query = self.remove_voc(query, "audio_only").strip()
        elif self.voc_match(query, "video_only"):
            query = self.remove_voc(query, "video_only")

        pred = self.media_intents.calc_intent(query)
        LOG.info(f"OVOSCommonPlay MediaType prediction: {pred}")
        LOG.debug(f"     utterance: {query}")
        intent = pred.get("name", "")
        if intent in self.intent2media:
            return self.intent2media[intent]
        LOG.debug("Generic OVOSCommonPlay query")
        return MediaType.GENERIC

    # playback control intents
    def handle_open(self, message):
        self.gui.show_home(app_mode=True)

    def handle_next(self, message):
        self.player.play_next()

    def handle_prev(self, message):
        self.player.play_prev()

    def handle_pause(self, message):
        self.player.pause()

    def handle_resume(self, message):
        """Resume playback if paused"""
        if self.player.state == PlayerState.PAUSED:
            self.player.resume()
        else:
            query = self.get_response("play.what")
            if query:
                message["utterance"] = query
                self.handle_play(message)

    def handle_play(self, message):
        utterance = message.data["utterance"]
        phrase = message.data.get("query", "") or utterance
        LOG.debug(f"Handle {message.msg_type} request: {phrase}")
        num = message.data.get("number", "")
        if num:
            phrase += " " + num

        # if media is currently paused, empty string means "resume playback"
        if self._should_resume(phrase):
            self.player.resume()
            return
        if not phrase:
            phrase = self.get_response("play.what")
            if not phrase:
                # TODO some dialog ?
                self.player.stop()
                self.gui.show_home(app_mode=True)
                return

        # classify the query media type
        media_type = self.classify_media(utterance)

        # search common play skills
        results = self._search(phrase, utterance, media_type)
        self._do_play(phrase, results, media_type)

    # "read XXX" - non "play XXX" audio book intent
    def handle_read(self, message):
        utterance = message.data["utterance"]
        phrase = message.data.get("query", "") or utterance
        # search common play skills
        results = self._search(phrase, utterance, MediaType.AUDIOBOOK)
        self._do_play(phrase, results, MediaType.AUDIOBOOK)

    def _do_play(self, phrase, results, media_type=MediaType.GENERIC):
        self.player.reset()
        LOG.debug(f"Playing {len(results)} results for: {phrase}")
        if not results:
            if self.gui:
                if self.gui.active_extension == "smartspeaker":
                    self.gui.display_notification("Sorry, no matches found", style="warning")
            
            self.speak_dialog("cant.play",
                              data={"phrase": phrase,
                                    "media_type": media_type})
            
            if self.gui:
                if "smartspeaker" not in self.gui.active_extension:
                    if not self.gui.persist_home_display:
                        self.gui.remove_homescreen()
                    else:
                        self.gui.remove_search_spinner()
                else:
                    self.gui.clear_notification()

        else:
            if self.gui:
                if self.gui.active_extension == "smartspeaker":
                    self.gui.display_notification("Found a match", style="success")
            
            best = self.player.media.select_best(results)
            self.player.play_media(best, results)

            if self.gui:
                if self.gui.active_extension == "smartspeaker":
                    self.gui.clear_notification()
            
            self.enclosure.mouth_reset()  # TODO display music icon in mk1
            self.set_context("Playing")

    def handle_stop(self, message=None):
        # will stop any playback in GUI and AudioService
        try:
            return self.player.stop()
        except:
            pass

    # helper methods
    def _search(self, phrase, utterance, media_type):
        self.enclosure.mouth_think()
        # check if user said "play XXX audio only/no video"
        audio_only = False
        video_only = False
        if self.voc_match(phrase, "audio_only"):
            audio_only = True
            # dont include "audio only" in search query
            phrase = self.remove_voc(phrase, "audio_only")
            # dont include "audio only" in media type classification
            utterance = self.remove_voc(utterance, "audio_only").strip()
        elif self.voc_match(phrase, "video_only"):
            video_only = True
            # dont include "video only" in search query
            phrase = self.remove_voc(phrase, "video_only")

        # Now we place a query on the messsagebus for anyone who wants to
        # attempt to service a 'play.request' message.
        results = []
        phrase = phrase or utterance
        for r in self.player.media.search(phrase, media_type=media_type):
            results += r["results"]
        LOG.debug(f"Got {len(results)} results")
        # ignore very low score matches
        results = [r for r in results
                   if r["match_confidence"] >= self.settings.get("min_score",
                                                                 50)]
        LOG.debug(f"Got {len(results)} usable results")

        # check if user said "play XXX audio only"
        if audio_only:
            LOG.info("audio only requested, forcing audio playback "
                     "unconditionally")
            for idx, r in enumerate(results):
                # force streams to be played audio only
                results[idx]["playback"] = PlaybackType.AUDIO
        # check if user said "play XXX video only"
        elif video_only:
            LOG.info("video only requested, filtering non-video results")
            for idx, r in enumerate(results):
                if results[idx]["media_type"] == MediaType.VIDEO:
                    # force streams to be played in video mode, even if
                    # audio playback requested
                    results[idx]["playback"] = PlaybackType.VIDEO
            # filter audio only streams
            results = [r for r in results
                       if r["playback"] == PlaybackType.VIDEO]
        # filter video results if GUI not connected
        elif not can_use_gui(self.bus):
            LOG.info("unable to use GUI, filtering non-audio results")
            # filter video only streams
            results = [r for r in results
                       if r["playback"] == PlaybackType.AUDIO]
        LOG.debug(f"Returning {len(results)} results")
        return results

    def _should_resume(self, phrase):
        if self.player.state == PlayerState.PAUSED:
            if not phrase.strip() or \
                    self.voc_match(phrase, "Resume", exact=True) or \
                    self.voc_match(phrase, "Play", exact=True):
                return True
        return False
