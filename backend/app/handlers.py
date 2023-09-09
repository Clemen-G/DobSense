import tornado
import logging
import uuid
import json
from alignment.coordinates import eq_to_alt_az

class AppHandler(tornado.web.RequestHandler):
    def initialize(self, globals):
        self.globals = globals

    # https://stackoverflow.com/questions/35254742/tornado-server-enable-cors-requests
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:8000")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')


class HandshakeHandler(AppHandler):
    # https://stackoverflow.com/questions/35254742/tornado-server-enable-cors-requests
    def options(self):
        self.set_status(204)
        self.finish()

    def post(self):
        logging.info(self.request.body)
        payload = json.loads(self.request.body)
        self.globals["location"] = payload["position"]
        self.write(dict(constellation_data=self.globals["constellation_data"]))

    def get(self):
        logging.info("hello")
        self.finish()


class AlignmentsHandler(AppHandler):
    def initialize(self, globals, telescope_interface):
        self.telescope_interface = telescope_interface
        return super().initialize(globals)

    def put(self):
        alignment = json.loads(self.request.body)
        alignment["id"] = str(uuid.uuid4())
        alignment_points = self.globals["alignment_points"]
        alignment_points.append(alignment)
        logging.info(f"Adding alignment point {alignment}")
        self._add_current_alt_az_coords(alignment)
        # logging.info(alignment_points)
        self.write(dict(alignment_points=alignment_points))

    def _add_current_alt_az_coords(self, alignment):
        logging.info(f"Aligning hip object {alignment['object_id']}")
        logging.info(f"Current location: {self.globals['location']}")
        logging.info(f"Alignment timestamp: {alignment['timestamp']}")

        ra_dec_coords = self.globals["stars"][alignment["object_id"]]["RA/DEC"]
        logging.info(f"  with RA/DEC {ra_dec_coords}")
        alt_az_coords = eq_to_alt_az(ra_dec_coords, 
                                     self.globals["location"],
                                     alignment["timestamp"])
        logging.info(f"Alt-az coordinates: az: {alt_az_coords.az.value}, alt: {alt_az_coords.alt.value}")
        taz_coords = self.telescope_interface.\
            get_telescope_angles_from_alt_az_angles(
                alt_az_coords.az.value,
                alt_az_coords.alt.value)
        logging.info(f"Taz coordinates: {taz_coords}")
        alignment["taz_coords"] = taz_coords

class AlignmentHandler(AppHandler):
    def get(self):
        self.set_status(200)
        self.finish()
