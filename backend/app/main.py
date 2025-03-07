import os
import sys
import logging
from logging import config as log_conf
import asyncio
import tornado
from handler import HandshakeHandler, AlignmentHandler, AlignmentsHandler
from handler import WebsocketHandler, ObjectsHandler, TargetHandler
from globals import GLOBALS
from tornado.options import define, options, parse_command_line
from alignment.telescope_interface import TelescopeInterface, generate_matrices
from alignment.alignment_finder import AlignmentFinder
from generated.gradients import gradient_optimized_err_lambda, gradient_penalties_lambda
from alignment.alignment_delegate import AlignmentDelegate
from key_reader import KeyReader
import initializer.astropy


logging_configuration = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "\033[32m[%(levelname)1.1s %(asctime)s.%(msecs)03d %(name)s:%(lineno)d]\033[0m %(message)s",
            "datefmt": "%Y%m%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}
log_conf.dictConfig(logging_configuration)

logger = logging.getLogger(__name__)
logger.info("Starting up")


alignment_finder = AlignmentFinder(
    gradient_optimized_err_lambda=gradient_optimized_err_lambda,
    gradient_penalties_lambda=gradient_penalties_lambda)

alignment_delegate = AlignmentDelegate(alignment_finder, GLOBALS)


async def main():
    logging.info("Setting astropy to offline mode")
    initializer.astropy.set_astropy_offline()

    key_reader = KeyReader()
    telescope_interface = TelescopeInterface(
        alignment_matrices=generate_matrices(),
        key_reader=key_reader)
    
    application = tornado.web.Application([
        (r"/api/handshake", HandshakeHandler,
            dict(globals=GLOBALS)),
        (r"/api/alignments", AlignmentsHandler,
            dict(globals=GLOBALS,
                telescope_interface=telescope_interface)),
        (r"/api/alignments/(?P<alignment_point_id>.+)", AlignmentsHandler,
            dict(globals=GLOBALS,
                telescope_interface=telescope_interface)),
        (r"/api/alignment", AlignmentHandler,
            dict(globals=GLOBALS,
                alignment_delegate=alignment_delegate)),
        (r"/api/target", TargetHandler,
            dict(globals=GLOBALS)),
        (r"/api/objects", ObjectsHandler,
            dict(globals=GLOBALS)),
        (r"/api/websocket", WebsocketHandler,
            dict(globals=GLOBALS,
                 telescope_interface=telescope_interface))
    ], debug=options.debug)

    # keyboard reader. Don't remove the assignment or the task might
    # be garbage collected.
    task = asyncio.create_task(key_reader.read_keys())

    server = tornado.web.HTTPServer(application)
    server.listen(os.environ.get("TORNADO_PORT", 8001))
    logger.info(sys.path)
    logger.info(os.getcwd())
    logger.info("ready")
    await asyncio.Event().wait()


if __name__ == "__main__":
    define("debug", default=False, help="run in debug mode", type=bool)
    parse_command_line()

    asyncio.run(main())
