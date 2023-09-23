import time
import json
import asyncio
import tornado
from tornado import websocket
import logging
import uuid
from exceptions import UserException
from alignment.coordinates import eq_to_alt_az
from data_model import AlignmentPoint, IsAligned, TelescopeCoords, TazCoords,\
    EqCoords
from data_model import AltAzCoords
import alignment.coordinates as coordinates


class AppHandler(tornado.web.RequestHandler):
    def initialize(self, globals):
        self.globals = globals

    # https://stackoverflow.com/questions/35254742/tornado-server-enable-cors-requests
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:8000")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
    
    def write_error(self, status_code, **kwargs):
        # kwargs: {'exc_info': 
        #    (<class 'exceptions.UserException'>,
        #    UserException(UserException(...), 'Alignment requires at least 3 distinct objects'),
        #    <traceback object at 0x7fb91e766940>)}

        logging.info("nuuush begin")
        if kwargs['exc_info'][0] == UserException:
            self.set_status(409)
            message = str(kwargs['exc_info'][1].user_message)
            self.write({"error_message": message})
            self.finish()


class HandshakeHandler(AppHandler):
    # https://stackoverflow.com/questions/35254742/tornado-server-enable-cors-requests
    def options(self):
        self.set_status(204)
        self.finish()

    def post(self):
        logging.info(self.request.body)
        payload = json.loads(self.request.body)
        if self.globals.state.location is None:
            self.globals.state.location = payload["position"]
        self.write(
            dict(constellation_data=self.globals.catalogs.constellations))

    def get(self):
        logging.info("hello")
        self.finish()


class AlignmentsHandler(AppHandler):
    def initialize(self, globals, telescope_interface):
        self.telescope_interface = telescope_interface
        return super().initialize(globals)

    def put(self):
        alignment_point = json.loads(self.request.body)
        alignment_point["id"] = str(uuid.uuid4())
        self._add_current_alt_az_coords(alignment_point)

        alignment_points = self.globals.state.alignment_points
        logging.info(f"Adding alignment point {alignment_point}")
        alignment_points.alignment_points.append(
            AlignmentPoint(**alignment_point))
        self.write(alignment_points.model_dump_json())

    def _add_current_alt_az_coords(self, alignment):
        logging.info(f"Aligning hip object {alignment['object_id']}")
        logging.info(f"Current location: {self.globals.state.location}")
        logging.info(f"Alignment timestamp: {alignment['timestamp']}")

        alignment_star = self.globals.catalogs.get_star_info(
            alignment["object_id"])
        logging.info(f"  with star {alignment_star}")
        alt_az_sky_coords = eq_to_alt_az(alignment_star["ra"],
                                     alignment_star["dec"],
                                     self.globals.state.location,
                                     alignment["timestamp"])
        alt_az_coords = AltAzCoords(az=alt_az_sky_coords.az.value,
                                    alt=alt_az_sky_coords.alt.value)
        logging.info(f"Alt-az coordinates: {alt_az_coords}")
        if alt_az_coords.alt < 0:
            raise UserException(409,
                                "Alignment objects must be above the horizon")
        taz_coords = (self.telescope_interface.get_taz_from_alt_az(
                alt_az_coords.az,
                alt_az_coords.alt))
        if taz_coords is None:
            raise UserException(409, "The scope can't point to this object")

        # simulator: "set" telescope angles to match aligned object
        self.telescope_interface.set_taz_coords(taz_coords)

        taz_coords = TazCoords(taz=taz_coords.taz, talt=taz_coords.talt)
        logging.info(f"Taz coordinates: {taz_coords}")
        alignment["taz_coords"] = taz_coords
        alignment["alt_az_coords"] = alt_az_coords


class AlignmentHandler(AppHandler):
    def initialize(self, globals, alignment_delegate):
        self.alignment_delegate = alignment_delegate
        return super().initialize(globals)

    def post(self):
        alignment_points = self.globals.state.alignment_points.alignment_points
        self._validate_get_input(alignment_points)
        self.alignment_delegate.start_alignment_procedure(alignment_points,
                                                          synchronous=True)
        self.set_status(200)
        self.finish()

    def _validate_get_input(self, alignment_points):
        if len(set((p.object_id for p in alignment_points))) < 3:
            raise UserException(http_code=400,
                                user_message="Alignment requires at least 3 distinct objects")


class WebsocketHandler(websocket.WebSocketHandler):
    def initialize(self, globals, telescope_interface):
        self.globals = globals
        self.telescope_interface = telescope_interface
        self.send_task = None
    
    def open(self):
        logging.info("WebSocket opened")

    def on_message(self, message_json):
        logging.info(message_json)
        message = json.loads(message_json)
        if message["messageType"] == "Hello":
            isAligned = self.globals.state.alignment_matrices is not None
            self.write_message(
                IsAligned(isTelescopeAligned=isAligned).model_dump_json())
            if self.send_task is None:
                self.send_task = asyncio.create_task(self._send_coordinates())
        else:
            raise ValueError(f"unexpected message {message}")

    def on_close(self):
        logging.info("WebSocket closed")
        if self.send_task:
            self.send_task.cancel()
            self.send_task = None

    def check_origin(self, origin):
        return True
    
    async def _send_coordinates(self):
        try:
            await self._do_send_coordinates()
        except Exception as e:
            logging.exception(e, exc_info=e)
            raise e

    async def _do_send_coordinates(self):
        SLEEP_INTERVAL = .5
        PING_INTERVAL = 10
        previous_is_aligned = False
        previous_taz_coords = None
        previous_time = 0
        while True:
            alignment_matrices = self.globals.state.alignment_matrices
            is_aligned = alignment_matrices is not None
            current_time = time.time()
            if is_aligned:
                current_taz_coords = self.telescope_interface.get_taz_coords()
                if (current_taz_coords != previous_taz_coords or
                    current_time - previous_time > PING_INTERVAL):
                    try:
                        taz_coords = TazCoords(
                            taz=current_taz_coords.taz,
                            talt=current_taz_coords.talt)
                        scope_az_coords = coordinates.taz_to_az(
                            alignment_matrices,
                            current_taz_coords.taz,
                            current_taz_coords.talt)
                        scope_az_coords = AltAzCoords(**scope_az_coords)
                        eq_coords = coordinates.alt_az_to_eq(
                            az=scope_az_coords.az,
                            alt=scope_az_coords.alt,
                            location=self.globals.state.location,
                            timestamp=current_time)
                        eq_coords = EqCoords(ra=eq_coords.ra.value,
                                             dec=eq_coords.dec.value)
                        scope_coords = TelescopeCoords(
                            taz_coords=taz_coords,
                            alt_az_coords=scope_az_coords,
                            eq_coords=eq_coords)
                        self.write_message(scope_coords.model_dump_json())
                        previous_taz_coords = current_taz_coords
                        previous_time = current_time
                    except websocket.WebSocketClosedError:
                        logging.warn("failed to send coordinates")
                        break
            if (is_aligned and not previous_is_aligned or
                   (current_time - previous_time > PING_INTERVAL)):
                try:
                    self.write_message(
                        IsAligned(isTelescopeAligned=is_aligned).model_dump_json())
                    previous_is_aligned = is_aligned
                    previous_time = current_time
                except websocket.WebSocketClosedError:
                    logging.warn("failed to send hello")
                    break
            try:
                await asyncio.sleep(SLEEP_INTERVAL)
            except asyncio.CancelledError as e:
                logging.info("_send_coordinates canceled")
                raise e
        print('I should not be here')