import json
import logging
import asyncio
from tornado import websocket
from alignment import coordinates
from data_model import AltAzCoords, EqCoords, HelloMessage, IsAlignedMessage
from data_model import TazCoords, TelescopeCoordsMessage, TelescopeCoords
from data_model import TargetCoordsMessage, TargetCoords, AlignmentPointsMessage
from globals import SystemState


class WebsocketHandler(websocket.WebSocketHandler):
    def initialize(self, globals, telescope_interface):
        self.globals = globals
        self.telescope_interface = telescope_interface
        self.send_task = None

    def open(self):
        logging.info("WebSocket opened")
        self.globals.state.register(
            SystemState.ALIGN_CHANGE,
            self._on_state_change)
        self.globals.state.register(
            SystemState.ALIGNMENT_POINTS_CHANGE,
            self._on_alignment_points_change)
        self.globals.state.register(
            SystemState.TARGET_CHANGE,
            self._on_state_change)

    def on_message(self, message_json):
        logging.info(message_json)
        message = json.loads(message_json)
        if message["messageType"] == "HelloMessage":
            self.globals.state.location = message["location"]
            self.globals.state.time = message["timestamp"]
            self._send_is_aligned()
            self._send_telescope_coords()
            self._send_target_coords()
            self._send_alignment_points()
            if self.send_task is None:
                self.send_task = asyncio.create_task(
                    self._send_coordinates_periodically())
        else:
            raise ValueError(f"unexpected message {message}")

    def on_close(self):
        logging.info("WebSocket closed")
        if self.send_task:
            self.send_task.cancel()
            self.send_task = None
        self.globals.state.unregister(
            SystemState.ALIGN_CHANGE,
            self._on_state_change)
        self.globals.state.unregister(
            SystemState.TARGET_CHANGE,
            self._on_state_change)
        self.globals.state.unregister(
            SystemState.ALIGNMENT_POINTS_CHANGE,
            self._on_alignment_points_change)

    def check_origin(self, origin):
        return True

    def _on_alignment_points_change(self, event_name):
        try:
            self._send_alignment_points()
        except websocket.WebSocketClosedError:
            logging.warn("Failed to send state change messages" +
                        "because websocket is closed")

    def _on_state_change(self, event_name):
        try:
            self._send_is_aligned()
            if self._is_aligned():
                self._send_telescope_coords()
                if self.globals.state.target:
                    self._send_target_coords()
        except websocket.WebSocketClosedError:
            logging.warn("Failed to send state change messages" +
                        "because websocket is closed")

    async def _send_coordinates_periodically(self):
        try:
            await self._do_send_coordinates()
        except Exception as e:
            logging.exception(e, exc_info=e)
            raise e

    async def _do_send_coordinates(self):
        SLEEP_INTERVAL = .5
        PING_INTERVAL = 10
        # avoid immediately resending the same messages on startup
        # since it's been done by on_message
        previous_taz_coords = self.telescope_interface.get_taz_coords()
        previous_system_time = self.globals.state.time
        while True:
            system_time = self.globals.state.time

            current_taz_coords = self.telescope_interface.get_taz_coords()
            if (current_taz_coords != previous_taz_coords or
                    system_time - previous_system_time > PING_INTERVAL):
                try:
                    # telescope coords message also functions as heartbeat
                    # so we send it inconditionally
                    self._send_telescope_coords()
                    if self.globals.state.target:
                        self._send_target_coords()
                    previous_taz_coords = current_taz_coords
                    previous_system_time = system_time
                except websocket.WebSocketClosedError:
                    logging.warn("failed to send coordinates")
                    break
            if (system_time - previous_system_time > PING_INTERVAL):
                try:
                    self._send_is_aligned()
                    previous_system_time = system_time
                except websocket.WebSocketClosedError:
                    logging.warn("failed to send hello")
                    break
            try:
                await asyncio.sleep(SLEEP_INTERVAL)
            except asyncio.CancelledError as e:
                logging.info("_send_coordinates canceled")
                raise e
        print('I should not be here')

    def _is_aligned(self):
        alignment_matrices = self.globals.state.alignment_matrices
        return alignment_matrices is not None

    def _send_is_aligned(self):
        """Sends a IsAligned message asynchronously.

            Throws websocket.WebSocketClosedError if the websocket is closed.
        """
        self.write_message(
            IsAlignedMessage(isTelescopeAligned=self._is_aligned()).model_dump_json())

    def _send_alignment_points(self):
        alignment_points = AlignmentPointsMessage(
            alignment_points=self.globals.state.alignment_points.get_all())
        self.write_message(alignment_points.model_dump_json())

    def _send_telescope_coords(self):
        """Sends a TelescopeCoords message asynchronously.

            Throws websocket.WebSocketClosedError if the websocket is closed.
        """
        if not self._is_aligned():
            self.write_message(TelescopeCoordsMessage(
                telescope_coords=None).model_dump_json())
            return

        current_taz_coords = self.telescope_interface.get_taz_coords()
        taz_coords = TazCoords(
            taz=current_taz_coords.taz,
            talt=current_taz_coords.talt)
        scope_az_coords = coordinates.taz_to_az(
            self.globals.state.alignment_matrices,
            current_taz_coords.taz,
            current_taz_coords.talt)
        scope_az_coords = AltAzCoords(**scope_az_coords)
        eq_coords = coordinates.alt_az_to_eq(
            az=scope_az_coords.az,
            alt=scope_az_coords.alt,
            location=self.globals.state.location,
            timestamp=self.globals.state.time)
        eq_coords = EqCoords(ra=eq_coords.ra.value,
                                dec=eq_coords.dec.value)
        scope_coords_msg = TelescopeCoordsMessage(
            telescope_coords=TelescopeCoords(
                taz_coords=taz_coords,
                alt_az_coords=scope_az_coords,
                eq_coords=eq_coords))

        self.write_message(scope_coords_msg.model_dump_json())

    def _send_target_coords(self):
        if not self._is_aligned() or self.globals.state.target is None:
            self.write_message(TargetCoordsMessage(
                target_coords=None).model_dump_json())
            return

        target_id = self.globals.state.target
        target_eq_coords = self.globals.catalogs.get_object_coords(target_id)

        alt_az_sky_coords = coordinates.eq_to_alt_az(target_eq_coords.ra,
                                     target_eq_coords.dec,
                                     self.globals.state.location,
                                     self.globals.state.time)

        alt_az_coords = AltAzCoords(az=alt_az_sky_coords.az.value,
                                    alt=alt_az_sky_coords.alt.value)
        taz_coords = (self.telescope_interface.get_taz_from_alt_az(
                alt_az_coords.az,
                alt_az_coords.alt))

        if taz_coords is None:
            raise Exception("Cannot determine taz_coords for the target")

        taz_coords = TazCoords(taz=taz_coords.taz, talt=taz_coords.talt)

        target_coords_msg = TargetCoordsMessage(
            target_coords=TargetCoords(object_id=target_id,
                                     eq_coords=target_eq_coords,
                                     alt_az_coords=alt_az_coords,
                                     taz_coords=taz_coords))

        self.write_message(target_coords_msg.model_dump_json())