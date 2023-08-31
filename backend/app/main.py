import os
import logging
import asyncio
import tornado
from handlers import *

from tornado.options import define, options, parse_command_line

async def main():
    application = tornado.web.Application([
        # the / url redirects to a landing page that will load the app manifest
        # (r"/()", tornado.web.StaticFileHandler, dict(path="./static", default_filename='landing.html')),
        # (r"/(manifest\.json)", tornado.web.StaticFileHandler, dict(path='.')),
        # (r"/static/(.+)", tornado.web.StaticFileHandler, dict(path='./static')),
        (r"/api/handshake", HandshakeHandler),
    ], debug=options.debug)

    server = tornado.web.HTTPServer(application)
    server.listen(os.environ.get("TORNADO_PORT", 8001))
    logging.info("ready")
    await asyncio.Event().wait()

if __name__ == "__main__":
    define("debug", default=False, help="run in debug mode", type=bool)
    parse_command_line()
    asyncio.run(main())
