from os.path import join, dirname
from time import sleep
from mycroft_bus_client.message import Message
from ovos_utils.gui import GUIInterface
from ovos_utils.log import LOG

from ovos_plugin_common_play.ocp.status import *


class OCPMediaPlayerGUI(GUIInterface):
    def __init__(self):
        # the skill_id is chosen so the namespace matches the regular bus api
        # ie, the gui event "XXX" is sent in the bus as "ovos.common_play.XXX"
        super(OCPMediaPlayerGUI, self).__init__(skill_id="ovos.common_play")
        self.ocp_skills = {}  # skill_id: meta

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

    @property
    def search_spinner_page(self):
        return join(self.player.res_dir, "ui", "BusyPage.qml")

    @property
    def search_screen_page(self):
        return join(self.player.res_dir, "ui", "Search.qml")

    @property
    def skills_page(self):
        return join(self.player.res_dir, "ui", "OCPSkillsView.qml")

    @property
    def audio_player_page(self):
        return join(self.player.res_dir, "ui", "OVOSAudioPlayer.qml")

    @property
    def audio_service_page(self):
        return join(self.player.res_dir, "ui", "OVOSSyncPlayer.qml")

    @property
    def video_player_page(self):
        return join(self.player.res_dir, "ui", "OVOSVideoPlayer.qml")

    @property
    def web_player_page(self):
        return join(self.player.res_dir, "ui", "OVOSWebPlayer.qml")

    @property
    def search_page(self):
        return join(self.player.res_dir, "ui", "Disambiguation.qml")

    @property
    def playlist_page(self):
        return join(self.player.res_dir, "ui", "Playlist.qml")

    def shutdown(self):
        self.bus.remove("ovos.common_play.playback_time",
                        self.handle_sync_seekbar)
        super().shutdown()

    # OCPMediaPlayer interface
    def update_ocp_skills(self):
        # trigger a presence announcement from all loaded ocp skills
        self.bus.emit(Message("ovos.common_play.skills.get"))
        sleep(0.2)
        skills_cards = [
            {"skill_id": skill["skill_id"],
             "title": skill["skill_name"],
             "image": skill["thumbnail"],
             "media_type": skill.get("media_type") or [MediaType.GENERIC]
        } for skill in self.ocp_skills.values() if skill["featured"]]

        skills_cards = [s for s in skills_cards
                        if MediaType.ADULT not in s["media_type"] and
                        MediaType.HENTAI not in s["media_type"]]

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
        self["allowUrlChange"] = False # TODO allow to be defined per track

    def update_search_results(self):
        self["searchModel"] = {
            "data": [e.infocard for e in self.player.disambiguation]
        }

    def update_playlist(self):
        self["playlistModel"] = {
            "data": [e.infocard for e in self.player.tracks]
        }

    def show_playback_error(self):
        # TODO error page
        self.show_text("Playback error")

    def show_search_spinner(self):
        self.clear()
        self["footer_text"] = "Querying Skills\n\n"
        self.show_page(self.search_spinner_page, override_idle=30)

    def show_home(self):
        self.update_ocp_skills()
        to_remove = [self.search_spinner_page,
                     self.video_player_page,
                     self.web_player_page,
                     self.audio_player_page,
                     self.audio_service_page]
        self.remove_pages([p for p in to_remove if p in self.pages])
        sleep(0.2)
        self.show_pages([self.search_screen_page, self.skills_page],
                        index=0, override_idle=True,
                        override_animations=True)

    def release(self):
        self.remove_pages(self.pages)
        super().release()

    def show_player(self):
        # remove old pages
        self.remove_pages(self._get_pages_to_rm())
        sleep(0.2)
        # show new pages
        self.show_pages(self._get_pages_to_display(),
                        index=0, override_idle=True,
                        override_animations=True)

    # page helpers
    def _get_player_page(self):
        if self.player.active_backend == PlaybackType.AUDIO_SERVICE or \
                self.player.settings.force_audioservice:
            return self.audio_service_page
        elif self.player.active_backend == PlaybackType.VIDEO:
            return self.video_player_page
        elif self.player.active_backend == PlaybackType.AUDIO:
            return self.audio_player_page
        elif self.player.active_backend == PlaybackType.WEBVIEW:
            return self.web_player_page
        elif self.player.active_backend == PlaybackType.MPRIS:
            return self.audio_service_page
        else:  # external playback (eg. skill)
            # TODO ?
            return self.audio_service_page

    def _get_pages_to_rm(self):
        to_remove = [self.search_spinner_page,
                     self.web_player_page]

        # remove old player pages
        to_remove += [p for p in (self.video_player_page,
                                  self.audio_player_page,
                                  self.audio_service_page)
                      if p != self._get_player_page()]

        # check if search_results / playlist pages should be displayed
        if self.player.active_backend in [PlaybackType.MPRIS]:
            # external player, no search or playlists
            to_remove += [self.search_page, self.playlist_page]
        else:
            if not len(self.player.disambiguation):
                to_remove.append(self.search_page)
            if not len(self.player.tracks):
                to_remove.append(self.playlist_page)

        # filter all active pages that fit the criteria
        return [p for p in to_remove if p in self.pages]

    def _get_pages_to_display(self):
        # determine pages to be shown
        pages = [self._get_player_page()]
        if len(self.player.disambiguation):
            pages.append(self.search_page)
        if len(self.player.tracks):
            pages.append(self.playlist_page)
        return pages

    # gui <-> playlists
    def handle_play_from_playlist(self, message):
        LOG.info("Playback requested from playlist results")
        media = message.data["playlistData"]
        for track in self.player.playlist:
            if track == media:  # found track
                self.player.play_media(track)
                break
        else:
            LOG.error("Track is not part of loaded playlist!")

    def handle_play_from_search(self, message):
        LOG.info("Playback requested from search results")
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
        self.show_page(self.search_page, override_idle=True)

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
            self.remove_pages([p for p in self.pages
                               if p != self.search_page])
            self.show_page(self.search_page, override_idle=60)

        # show search input page
        else:
            self.remove_pages([p for p in self.pages
                               if p != self.search_screen_page])
            self.show_page(self.search_screen_page, override_idle=60)
