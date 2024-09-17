import time
from os.path import join, dirname, isfile
from threading import Event, Lock
from typing import Optional, List
from ovos_config import Configuration
from ovos_plugin_common_play.ocp.gui import OCPMediaPlayerGUI
from ovos_plugin_common_play.ocp.player import OCPMediaPlayer
from ovos_utils.gui import can_use_gui
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message

from padacioso import IntentContainer

from ovos_workshop import OVOSAbstractApplication
from ovos_workshop.decorators.ocp import *
from ovos_plugin_manager.ocp import load_stream_extractors

from ovos_plugin_common_play.ocp.constants import OCP_ID


class OCP(OVOSAbstractApplication):
    def __init__(self, bus=None, lang=None, settings=None, skill_id=OCP_ID,
                 validate_source: bool = True,
                 native_sources: Optional[List[str]] = None):
        # settings = settings or OCPSettings()
        res_dir = join(dirname(__file__), "res")
        super().__init__(skill_id=skill_id, resources_dir=res_dir,
                         bus=bus, lang=lang, gui=OCPMediaPlayerGUI(bus=bus))
        if settings:
            LOG.debug(f"Updating settings from value passed at init")
            self.settings.merge(settings)

        self.player = OCPMediaPlayer(bus=self.bus,
                                     lang=self.lang,
                                     settings=self.settings,
                                     resources_dir=res_dir,
                                     gui=self.gui,
                                     skill_id=OCP_ID,
                                     validate_source=validate_source,
                                     native_sources=native_sources)
        self.register_ocp_api_events()
        LOG.info("Using Classic OCP with experimental OCP pipeline")
        # report available plugins to ovos-core pipeline
        self.handle_get_SEIs(Message("ovos.common_play.SEI.get"))

    def handle_ping(self, message):
        """
        Handle ovos.common_play.ping Messages and emit a response
        @param message: message associated with request
        """
        self.bus.emit(message.reply("ovos.common_play.pong"))

    def register_ocp_api_events(self):
        """
        Register messagebus handlers for OCP events
        """
        self.add_event('ovos.common_play.SEI.get', self.handle_get_SEIs)
        self.add_event("ovos.common_play.ping", self.handle_ping)
        self.add_event('ovos.common_play.home', self.handle_home)

    def handle_get_SEIs(self, message):
        """report available StreamExtractorIds

        Ported from ovos-media to accommodate migration period
        and making old OCP compatible with the new pipeline

        OCP plugins handle specific SEIs and return a real stream / extra metadata

        this moves parsing to playback time instead of search time

        SEIs are identifiers of the format "{SEI}//{uri}"
        that might be present in media results

        seis are NOT uris, a uri comes after {SEI}//

        eg. for the youtube plugin a skill can return
          "youtube//https://youtube.com/watch?v=wChqNkd6F24"
        """
        xtract = load_stream_extractors()  # @lru_cache, its a lazy loaded singleton
        self.bus.emit(message.response({"SEI": xtract.supported_seis}))

    def handle_home(self, message=None):
        """
        Handle ovos.common_play.home Messages and show the homescreen
        @param message: message associated with request
        """
        # homescreen / launch from .desktop
        self.gui.show_home(app_mode=True)

    def default_shutdown(self):
        self.player.shutdown()

