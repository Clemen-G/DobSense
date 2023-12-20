import json
import logging
import uuid
from .AppHandler import AppHandler
from alignment import coordinates
from data_model import AlignmentPoint, AltAzCoords, TazCoords
from exceptions import UserException


class AlignmentsHandler(AppHandler):
    def initialize(self, globals, telescope_interface):
        self.telescope_interface = telescope_interface
        return super().initialize(globals)

    def put(self):
        if not self.globals.state.time or not self.globals.state.location:
            raise UserException(409, "Time/location not yet established")
        alignment_point = json.loads(self.request.body)
        alignment_point["id"] = str(uuid.uuid4())
        alignment_point["timestamp"] = self.globals.state.time
        self._add_current_alt_az_coords(alignment_point)

        logging.info(f"Adding alignment point {alignment_point}")
        self.globals.state.alignment_points.add(
            AlignmentPoint(**alignment_point))
        self.write("")

    def delete(self, alignment_point_id):
        alignment_point_id = self.path_kwargs["alignment_point_id"]
        logging.info(f"Deleting alignment point {alignment_point_id}")
        self.globals.state.alignment_points.delete(alignment_point_id)
        self.write("")
    
    def _add_current_alt_az_coords(self, alignment):
        logging.info(f"Aligning hip object {alignment['object_id']}")
        logging.info(f"Current location: {self.globals.state.location}")
        logging.info(f"Alignment timestamp: {alignment['timestamp']}")

        alignment_star = self.globals.catalogs.get_star_info(
            alignment["object_id"])
        logging.info(f"  with star {alignment_star}")
        alt_az_sky_coords = coordinates.eq_to_alt_az(alignment_star["ra"],
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

        # simulator: "set" telescope angles to match aligned object
        self.telescope_interface.set_taz_coords(taz_coords)

        taz_coords = TazCoords(taz=taz_coords.taz, talt=taz_coords.talt)
        logging.info(f"Taz coordinates: {taz_coords}")
        alignment["taz_coords"] = taz_coords
        alignment["alt_az_coords"] = alt_az_coords