import os
import logging
import asyncio
import json
import tornado
from handlers import HandshakeHandler, AlignmentHandler, AlignmentsHandler


from tornado.options import define, options, parse_command_line
GLOBALS = {
    "location": None,
    "alignment_points": [],
    "constellation_data": None,
    "app_path": os.path.dirname(os.path.realpath(__file__))
}


async def main():
    application = tornado.web.Application([
        (r"/api/handshake", HandshakeHandler, dict(globals=GLOBALS)),
        (r"/api/alignments", AlignmentsHandler, dict(globals=GLOBALS)),
        (r"/api/alignment", AlignmentHandler, dict(globals=GLOBALS)),
    ], debug=options.debug)

    server = tornado.web.HTTPServer(application)
    server.listen(os.environ.get("TORNADO_PORT", 8001))
    logging.info("ready")
    await asyncio.Event().wait()


def load_constellation_data():
    with open(GLOBALS["app_path"] + "/../data/constellations_stars.json") as f:
        GLOBALS["constellation_data"] = json.load(f)


if __name__ == "__main__":
    define("debug", default=False, help="run in debug mode", type=bool)
    parse_command_line()

    load_constellation_data()
    asyncio.run(main())
