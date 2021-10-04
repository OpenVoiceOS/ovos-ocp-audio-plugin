import asyncio
from threading import Thread, Event
from time import sleep

from dbus_next.aio import MessageBus as DbusMessageBus
from dbus_next.message import Message as DbusMessage, \
    MessageType as DbusMessageType
from ovos_plugin_common_play.ocp.status import TrackState, PlaybackType, \
    PlayerState
from ovos_utils.log import LOG


class MprisPlayerCtl(Thread):
    def __init__(self, daemonic=True):
        super(MprisPlayerCtl, self).__init__()
        self.dbus = None
        self.loop = asyncio.get_event_loop()

        self.setDaemon(daemonic)
        self.shutdown_event = Event()
        self.stop_event = Event()
        self.pause_event = Event()
        self.resume_event = Event()
        self.next_event = Event()
        self.prev_event = Event()

        self.main_player = None
        self.players = {}
        self.player_meta = {}

        self._ocp_player = None

    def bind(self, ocp_player):
        self._ocp_player = ocp_player
        self.start()

    def _update_ocp(self):
        if self.stop_event.is_set():
            return
        if self._ocp_player and self.player_meta.get(self.main_player):
            data = self.player_meta[self.main_player]
            if self._ocp_player.active_skill != self.main_player:
                # reset ocp, it will display metadata of current track
                self._ocp_player.reset()

                # show GUI if player changed
                self._ocp_player.gui.show_player()

            # update ocp metadata
            data["skill_id"] = data["external_player"]
            data["bg_image"] = data.get("image")
            data["playback"] = PlaybackType.MPRIS
            data["status"] = TrackState.PLAYING_MPRIS

            self._ocp_player.set_now_playing(data)
            state = data.get("state") or "Playing"
            if state == "Paused":
                self._ocp_player.set_player_state(PlayerState.PAUSED)
            elif state == "Playing":
                self._ocp_player.set_player_state(PlayerState.PLAYING)
            else:
                self._ocp_player.set_player_state(PlayerState.STOPPED)
            self._ocp_player.repeat = data.get("repeat") or \
                                      self._ocp_player.repeat
            self._ocp_player.shuffle = data.get("shuffle") or \
                                       self._ocp_player.shuffle

    async def handle_new_player(self, data):
        LOG.info(f"Found MPRIS Player: {data['name']}")

    async def handle_player_status(self, data):
        # LOG.debug(f'Player Info: {data}')
        if data.get("state") == 'Playing':
            await self._set_main_player(data["external_player"])
        elif data["external_player"] == self.main_player:
            self._update_ocp()

    async def _set_main_player(self, name):
        self.main_player = name
        self._update_ocp()
        # if there are multiple external players playing, stop the
        # previous ones!
        # TODO config option disabled by default!
        for p in self.players:
            if p != name:
                await self._stop_player(p)

    async def _play_prev(self, name, max_tries=1):
        if name not in self.players:
            LOG.error(f"Invalid player: {name}")
            return
        try:
            if self.player_meta[name]["state"] == "Playing":
                LOG.debug(f"player previous {name}")
                player = self.players[name].get_interface(
                    'org.mpris.MediaPlayer2.Player')
                await player.call_previous()
        except:
            max_tries -= 1
            if max_tries > 0:
                await self._play_prev(name, max_tries)
            else:
                LOG.warning(f"player {name} does not support Previous")

    async def _play_next(self, name, max_tries=1):
        if name not in self.players:
            LOG.error(f"Invalid player: {name}")
            return
        try:
            if self.player_meta[name]["state"] == "Playing":
                LOG.debug(f"player next {name}")
                player = self.players[name].get_interface(
                    'org.mpris.MediaPlayer2.Player')
                await player.call_next()
        except:
            max_tries -= 1
            if max_tries > 0:
                await self._play_next(name, max_tries)
            else:
                LOG.warning(f"player {name} does not support Next")

    async def _pause_player(self, name, max_tries=1):
        if name not in self.players:
            LOG.error(f"Invalid player: {name}")
            return
        try:
            if self.player_meta[name]["state"] == "Playing":
                LOG.debug(f"pausing player {name}")
                player = self.players[name].get_interface(
                    'org.mpris.MediaPlayer2.Player')
                await player.call_pause()
        except:
            max_tries -= 1
            if max_tries > 0:
                await self._pause_player(name, max_tries)
            else:
                LOG.warning(f"player {name} can not be paused")

    async def _resume_player(self, name, max_tries=1):
        if name not in self.players:
            LOG.error(f"Invalid player: {name}")
            return
        try:
            if self.player_meta[name]["state"] != "Playing":
                LOG.debug(f"resuming player {name}")
                player = self.players[name].get_interface(
                    'org.mpris.MediaPlayer2.Player')
                await player.call_play()
        except:
            max_tries -= 1
            if max_tries > 0:
                await self._resume_player(name, max_tries)
            else:
                LOG.warning(f"player {name} can not be resumed")

    async def _stop_player(self, name, max_tries=1):
        if name not in self.players:
            LOG.error(f"Invalid player: {name}")
            return
        try:
            if self.player_meta[name]["state"] == "Playing":
                LOG.debug(f"stopping player {name}")
                player = self.players[name].get_interface(
                    'org.mpris.MediaPlayer2.Player')
                await player.call_stop()
        except:
            max_tries -= 1
            if max_tries > 0:
                await self._stop_player(name, max_tries)
            else:
                LOG.warning(f"player {name} can not be stopped")
        if name == self.main_player:
            self.main_player = None

    async def _stop_all(self):
        for p in self.players:
            await self._stop_player(p)

    async def _pause_all(self):
        for p in self.players:
            await self._pause_player(p)

    async def scan_players(self):
        reply = await self.dbus.call(
            DbusMessage(destination='org.freedesktop.DBus',
                        path='/org/freedesktop/DBus',
                        interface='org.freedesktop.DBus',
                        member='ListNames'))

        if reply.message_type == DbusMessageType.ERROR:
            raise Exception(reply.body[0])

        players = []
        for name in reply.body[0]:
            if "org.mpris.MediaPlayer2" in name:
                if name in self.players:
                    continue
                await self.handle_new_player({"name": name})
                introspection = await self.dbus.introspect(
                    name, '/org/mpris/MediaPlayer2')
                self.players[name] = self.dbus.get_proxy_object(
                    name, '/org/mpris/MediaPlayer2', introspection)
                self._create_player_handler(name)
                await self.query_player(name)
        return players

    def _create_player_handler(self, name):
        player = self.players[name]
        try:
            properties = player.get_interface(
                'org.freedesktop.DBus.Properties')
        except:
            # chromium
            LOG.warning(f"Player {name} does not allow reading properties")
            return

        # listen to signals
        async def on_properties_changed(interface_name,
                                  changed_properties,
                                  invalidated_properties):
            for changed, variant in changed_properties.items():
                player_name = properties.bus_name
                if changed == "PlaybackStatus":
                    state = self.player_meta[player_name].get("state")
                    if state != variant.value or not state:
                        self.player_meta[player_name]["state"] = variant.value
                        await self.handle_player_status(
                            {"state":  variant.value,
                             "external_player": player_name})
                elif changed == "Metadata":
                    await self.update_player_meta(player_name, variant.value)
                elif changed == "Shuffle":
                    self.player_meta[player_name]["shuffle"] = variant.value
                elif changed == "LoopStatus":
                    if variant.value == "Playlist" or variant.value == "Track":
                        self.player_meta[player_name]["repeat"] = True
                    else:
                        self.player_meta[player_name]["repeat"] = False
                # else:
                #    LOG.debug(f'{changed} - {variant.value}')

        properties.on_properties_changed(on_properties_changed)

    async def update_player_meta(self, name, meta):
        ocp_data = {"external_player": name}

        # these are injected when player is queried
        ocp_data["state"] = meta.get("state")
        ocp_data["repeat"] = meta.get("repeat")

        for k, v in meta.items():
            if k == "xesam:title":
                ocp_data["title"] = v.value
            elif k == "xesam:artist":
                ocp_data["artist"] = v.value[0]
            elif k == "xesam:album":
                ocp_data["album"] = v.value
            elif k == "mpris:artUrl":
                ocp_data["image"] = v.value
            elif k == "mpris:length":
                ocp_data["length"] = v.value

        self.player_meta[name] = ocp_data
        await self.handle_player_status(ocp_data)

    async def query_player(self, name):
        if name not in self.players:
            LOG.error(f"Invalid player: {name}")
            return
        try:
            player = self.players[name].get_interface(
                'org.mpris.MediaPlayer2.Player')
            meta = await player.get_metadata()
            meta["external_player"] = name
            try:
                meta["state"] = await player.get_playback_status()
            except:  # dbus_next.errors.DBusError
                pass
            try:
                loop_status = await player.get_loop_status()
                if loop_status == "None":
                    # The playback will stop when there are no more tracks to play
                    meta["repeat"] = False
                elif loop_status == "Track":
                    # The current track will start again from the begining once it has finished playing
                    meta["repeat"] = True
                elif loop_status == "Playlist":
                    # The playback loops through a list of tracks
                    meta["repeat"] = True
            except AttributeError:
                pass  # not all players expose this
            await self.update_player_meta(name, meta)
        except Exception as e:  # chromium
            LOG.error(f"failed to query player {name}")

    async def event_loop(self):
        self.shutdown_event.clear()
        self.stop_event.clear()
        self.pause_event.clear()

        if not self.dbus:
            self.dbus = await DbusMessageBus().connect()

        while not self.shutdown_event.is_set():
            # ocp requests to manipulate external players
            if self.stop_event.is_set():
                await self._stop_all()
                self.stop_event.clear()

            if self.pause_event.is_set():
                await self._pause_all()
                self.pause_event.clear()

            if self.prev_event.is_set():
                await self._play_prev(self.main_player)
                self.prev_event.clear()

            if self.next_event.is_set():
                await self._play_next(self.main_player)
                self.next_event.clear()

            if self.resume_event.is_set():
                await self._resume_player(self.main_player)
                self.resume_event.clear()

            # scan for new external players
            await self.scan_players()
            sleep(1)  # TODO configurable time between checks

            # sync player meta, not all players send all events properly...
            # eg, firefox videos do not send events if they autoplay, only if
            # you click the play button
            for player in self.players:
                await self.query_player(player)
            sleep(1)  # TODO configurable time between checks

    def run(self):
        self.loop.run_until_complete(self.event_loop())

    def play_prev(self):
        self.prev_event.set()

    def play_next(self):
        self.next_event.set()

    def resume(self):
        self.resume_event.set()

    def pause(self):
        self.pause_event.set()

    def stop(self):
        self.stop_event.set()

    def shutdown(self):
        self.stop()
        self.shutdown_event.set()
        self.loop.stop()
        while self.loop.is_running():
            sleep(0.2)
        self.loop.close()
