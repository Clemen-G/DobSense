import json
import logging
from .AppHandler import AppHandler
from alignment import coordinates
from exceptions import UserException


logger = logging.getLogger(__name__)


class TargetHandler(AppHandler):
    def put(self):
        request_body = json.loads(self.request.body)
        logger.info(request_body)
        object_id = request_body["object_id"]

        if not self.globals.state.alignment_matrices:
            raise UserException(http_code=409,
                                user_message="Cannot set target: telescope not aligned")

        object_eq_coords = self.globals.catalogs.get_object_coords(object_id)
        if not object_eq_coords:
            raise UserException(http_code=409,
                                user_message="Target not found")

        alt_az_sky_coords = coordinates.eq_to_alt_az(object_eq_coords.ra,
                                     object_eq_coords.dec,
                                     self.globals.state.location,
                                     self.globals.state.time)
        if alt_az_sky_coords.alt.value < 0:
            raise UserException(http_code=409,
                                user_message="Cannot set target: object below the horizon")

        self.globals.state.target = object_id