import tornado
import logging
import uuid
import json


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
        self.globals["position"] = payload["position"]
        self.write(dict(constellation_data=self.globals["constellation_data"]))

    def get(self):
        logging.info("hello")
        self.finish()


class AlignmentsHandler(AppHandler):
    def put(self):
        alignment = json.loads(self.request.body)
        alignment["id"] = str(uuid.uuid4())
        alignment_points = self.globals["alignment_points"]
        alignment_points.append(alignment)
        logging.info(alignment_points)
        self.write(dict(alignment_points=alignment_points))


class AlignmentHandler(AppHandler):
    def get(self):
        self.set_status(200)
        self.finish()
