import json
import logging
from .AppHandler import AppHandler
from data_model import Location


logger = logging.getLogger(__name__)


class HandshakeHandler(AppHandler):
    # https://stackoverflow.com/questions/35254742/tornado-server-enable-cors-requests
    def options(self):
        self.set_status(204)
        self.finish()

    def post(self):
        logger.info(self.request.body)
        payload = json.loads(self.request.body)
        self.globals.state.location = payload["location"]
        self.globals.state.time = payload["datetime"]
        self.write(
            dict(constellation_data=self.globals.catalogs.constellations))

    def get(self):
        logger.info("Hello")
        self.finish()