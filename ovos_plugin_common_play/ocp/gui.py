import enum
from abc import abstractmethod
from os.path import join, dirname
from threading import Timer

from mycroft_bus_client.message import Message
from ovos_config import Configuration
from ovos_utils.events import EventSchedulerInterface
from ovos_utils.gui import GUIInterface
from ovos_utils.log import LOG

from ovos_plugin_common_play.ocp import OCP_ID
from ovos_plugin_common_play.ocp.status import *


class OCPGUIState(str, enum.Enum):
    HOME = "home"
    APPS = "apps"  # skill selection menu
    SYNC_PLAYER = "sync_player"  # just show metadata
    AUDIO_PLAYER = "audio_player"  # handle playback gui side
    VIDEO_PLAYER = "video_player"  # handle playback gui side
    WEB_PLAYER = "web_player"  # playback is a web page (eg, iframe)
    PLAYLIST = "playlist"
    DISAMBIGUATION = "disambiguation"
    SPINNER = "spinner"
    PLAYBACK_ERROR = "playback_error"
    EXTRA = "extra"  # skill that provided selected media


class AbstractOCPMediaPlayerGUI(GUIInterface):
    def __init__(self):
        # the skill_id is chosen so the namespace matches the regular bus api
        # ie, the gui event "XXX" is sent in the bus as "ovos.common_play.XXX"
        super(AbstractOCPMediaPlayerGUI, self).__init__(skill_id=OCP_ID)
        self.ocp_skills = {}  # skill_id: meta
        core_config = Configuration()
        enclosure_config = core_config.get("gui") or {}
        self.active_extension = enclosure_config.get("extension", "generic")
        self.notification_timeout = None
        self.search_mode_is_app = False
        self.persist_home_display = False
        self.event_scheduler_interface = None

    def bind(self, player):
        self.player = player
        super().set_bus(self.bus)
        self.player.add_event("ovos.common_play.playback_time",
                              self.handle_sync_seekbar)
        self.player.add_event('ovos.common_play.playlist.play',
                              self.handle_play_from_playlist)
        self.player.add_event('ovos.common_play.search.play',
                              self.handle_play_from_search)
        self.player.add_event('ovos.common_play.skill.play',
                              self.handle_play_skill_featured_media)
        self.event_scheduler_interface = EventSchedulerInterface(name=OCP_ID,
                                                                 bus=self.bus)

    def release(self):
        self.clear()
        super().release()

    # OCPMediaPlayer interface
    def update_ocp_skills(self):
        skills_cards = [
            {"skill_id": skill["skill_id"],
             "title": skill["skill_name"],
             "image": skill["thumbnail"],
             "media_type": skill.get("media_type") or [MediaType.GENERIC]
             } for skill in self.player.media.get_featured_skills()]
        self["skillCards"] = skills_cards

    def update_seekbar_capabilities(self):
        self["canResume"] = True
        self["canPause"] = True
        self["canPrev"] = self.player.can_prev
        self["canNext"] = self.player.can_next

        if self.player.loop_state == LoopState.NONE:
            self["loopStatus"] = "None"
        elif self.player.loop_state == LoopState.REPEAT_TRACK:
            self["loopStatus"] = "RepeatTrack"
        elif self.player.loop_state == LoopState.REPEAT:
            self["loopStatus"] = "Repeat"

        if self.player.active_backend == PlaybackType.MPRIS:
            self["loopStatus"] = "None"
            self["shuffleStatus"] = False
        else:
            self["shuffleStatus"] = self.player.shuffle

    def update_current_track(self):
        self.update_seekbar_capabilities()

        self["media"] = self.player.now_playing.info
        self["uri"] = self.player.now_playing.uri
        self["title"] = self.player.now_playing.title
        self["image"] = self.player.now_playing.image or \
                        join(dirname(__file__), "res/ui/images/ocp.png")
        self["artist"] = self.player.now_playing.artist
        self["bg_image"] = self.player.now_playing.bg_image or \
                           join(dirname(__file__), "res/ui/images/ocp_bg.png")
        self["duration"] = self.player.now_playing.length
        self["position"] = self.player.now_playing.position
        # options below control the web player
        # javascript can be executed on page load and page behaviour modified
        # default values provide crude protection against ads and popups
        # TODO default permissive or restrictive?
        self["javascript"] = self.player.now_playing.javascript
        self["javascriptCanOpenWindows"] = False  # TODO allow to be defined per track
        self["allowUrlChange"] = False  # TODO allow to be defined per track

    def update_search_results(self):
        self["searchModel"] = {
            "data": [e.infocard for e in self.player.disambiguation]
        }

    def update_playlist(self):
        self["playlistModel"] = {
            "data": [e.infocard for e in self.player.tracks]
        }

    # GUI
    def manage_display(self, page_requested, timeout=None):
        # handle any state management needed before render
        self.prepare_display()

        if page_requested == OCPGUIState.HOME:
            self.prepare_home()
            self.render_home()
        elif page_requested == OCPGUIState.SYNC_PLAYER:
            self.prepare_sync_player()
            self.render_sync_player()
        elif page_requested == OCPGUIState.AUDIO_PLAYER:
            self.prepare_audio_player()
            self.render_audio_player()
        elif page_requested == OCPGUIState.VIDEO_PLAYER:
            self.prepare_video_player()
            self.render_video_player()
        elif page_requested == OCPGUIState.WEB_PLAYER:
            self.prepare_web_player()
            self.render_web_player()
        elif page_requested == OCPGUIState.PLAYLIST:
            self.prepare_playlist()
            self.render_playlist(timeout)
        elif page_requested == OCPGUIState.DISAMBIGUATION:
            self.prepare_search()
            self.render_disambiguation(timeout)
        elif page_requested == OCPGUIState.SPINNER:
            self.prepare_search_spinner()
            self.render_search_spinner()
        elif page_requested == OCPGUIState.PLAYBACK_ERROR:
            self.prepare_playback_error()
            self.render_playback_error()

        if (self.player.app_view_timeout_enabled
                and page_requested == "player"
                and self.player.app_view_timeout_mode == "all"):
            self.schedule_app_view_timeout()

    def remove_homescreen(self):
        self.release()

    # OCP pre-rendering abstract methods
    @abstractmethod
    def prepare_display(self):
        pass

    def prepare_home(self, app_mode=True):
        self.update_ocp_skills()  # populate self["skillCards"]

    def prepare_audio_player(self):
        self.prepare_sync_player()

    def prepare_video_player(self):
        self.prepare_sync_player()

    def prepare_sync_player(self):
        self.remove_search_spinner()
        self.clear_notification()
        self.update_current_track()  # populate now_playing metadata

    def prepare_web_player(self):
        self.prepare_sync_player()

    def prepare_playlist(self):
        self.update_playlist()  # populate self["playlistModel"]

    def prepare_search(self):
        self.update_search_results()  # populate self["searchModel"]

    @abstractmethod
    def prepare_search_spinner(self):
        pass

    @abstractmethod
    def prepare_playback_error(self):
        pass

    # OCP rendering abstract methods
    @abstractmethod
    def render_home(self):
        pass

    @abstractmethod
    def render_audio_player(self):
        pass

    @abstractmethod
    def render_video_player(self):
        pass

    @abstractmethod
    def render_sync_player(self):
        pass

    @abstractmethod
    def render_web_player(self):
        pass

    @abstractmethod
    def render_playlist(self, timeout=None):
        pass

    @abstractmethod
    def render_disambiguation(self, timeout=None):
        pass

    @abstractmethod
    def render_playback_error(self):
        pass

    @abstractmethod
    def render_search_spinner(self, persist_home=False):
        pass

    @abstractmethod
    def remove_search_spinner(self):
        pass

    # app view timeout
    def cancel_app_view_timeout(self, restart=False):
        self.event_scheduler_interface.cancel_scheduled_event("ocp_app_view_timer")
        if restart:
            self.schedule_app_view_timeout()

    def schedule_app_view_pause_timeout(self):
        if (self.player.app_view_timeout_enabled
                and self.player.app_view_timeout_mode == "pause"
                and self.player.state == PlayerState.PAUSED):
            self.schedule_app_view_timeout()

    def schedule_app_view_timeout(self):
        self.event_scheduler_interface.schedule_event(
            self.timeout_app_view, self.player.app_view_timeout_value,
            data=None, name="ocp_app_view_timer")

    def timeout_app_view(self):
        self.bus.emit(Message("homescreen.manager.show_active"))

    # notification / spinner
    def display_notification(self, text, style="info"):
        """ Display a notification on the screen instead of spinner on platform that support it """
        self.show_controlled_notification(text, style=style)
        self.reset_timeout_notification()

    def clear_notification(self):
        """ Remove the notification on the screen """
        if self.notification_timeout:
            self.notification_timeout.cancel()
        self.remove_controlled_notification()

    def start_timeout_notification(self):
        """ Remove the notification on the screen after 1 minute of inactivity """
        self.notification_timeout = Timer(60, self.clear_notification).start()

    def reset_timeout_notification(self):
        """ Reset the timer to remove the notification """
        if self.notification_timeout:
            self.notification_timeout.cancel()
        self.start_timeout_notification()

    # gui <-> playlists
    def handle_play_from_playlist(self, message):
        LOG.debug("Playback requested from playlist results")
        media = message.data["playlistData"]
        for track in self.player.playlist:
            if track == media:  # found track
                self.player.play_media(track)
                break
        else:
            LOG.error("Track is not part of loaded playlist!")

    def handle_play_from_search(self, message):
        LOG.debug("Playback requested from search results")
        media = message.data["playlistData"]
        for track in self.player.disambiguation:
            if track == media:  # found track
                self.player.play_media(track)
                break
        else:
            LOG.error("Track is not part of search results!")

    def handle_play_skill_featured_media(self, message):
        skill_id = message.data["skill_id"]
        LOG.debug(f"Featured Media request: {skill_id}")
        playlist = message.data["playlist"]

        self.player.playlist.clear()
        self.player.media.replace(playlist)
        self["displaySuggestionBar"] = False

        self.manage_display(OCPGUIState.DISAMBIGUATION)

    # audio_only service -> gui
    def handle_sync_seekbar(self, message):
        """ event sent by ovos audio_only backend plugins """
        self["length"] = message.data["length"]
        self["position"] = message.data["position"]

    # media player -> gui
    def handle_end_of_playback(self, message=None):
        show_results = False
        try:
            if len(self["searchModel"]["data"]):
                show_results = True
        except:
            pass

        # show search results, release screen after 60 seconds
        if show_results:
            self.manage_display(OCPGUIState.PLAYLIST, timeout=60)
