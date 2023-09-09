import os
import sys
import logging
import asyncio
import json
import tornado
from handlers import HandshakeHandler, AlignmentHandler, AlignmentsHandler
from tornado.options import define, options, parse_command_line
from alignment.telescope_interface import TelescopeInterface, generate_matrices

telescope_interface = TelescopeInterface(**generate_matrices())

GLOBALS = {
    "location": None,
    "alignment_points": [],
    "constellation_data": None,
    "stars": None,
    "app_path": os.path.dirname(os.path.realpath(__file__))
}


async def main():
    application = tornado.web.Application([
        (r"/api/handshake", HandshakeHandler, dict(globals=GLOBALS)),
        (r"/api/alignments",
         AlignmentsHandler,
         dict(globals=GLOBALS,
              telescope_interface=telescope_interface)),
        (r"/api/alignment", AlignmentHandler, dict(globals=GLOBALS)),
    ], debug=options.debug)

    server = tornado.web.HTTPServer(application)
    server.listen(os.environ.get("TORNADO_PORT", 8001))
    logging.info(sys.path)
    logging.info(os.getcwd())
    logging.info("ready")
    await asyncio.Event().wait()


def load_constellation_data():
    with open(GLOBALS["app_path"] + "/../data/constellations_stars.json") as f:
        GLOBALS["constellation_data"] = json.load(f)
        GLOBALS["stars"] = {
            obj["HIP"]: obj
                for const in GLOBALS["constellation_data"]
                    for obj in const["stars"]}


if __name__ == "__main__":
    define("debug", default=False, help="run in debug mode", type=bool)
    parse_command_line()

    load_constellation_data()
    asyncio.run(main())
