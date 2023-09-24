import os
import sys
import logging
import asyncio
import tornado
from handlers import HandshakeHandler, AlignmentHandler, AlignmentsHandler, ObjectsHandler
from handlers import WebsocketHandler
from globals import GLOBALS
from tornado.options import define, options, parse_command_line
from alignment.telescope_interface import TelescopeInterface, generate_matrices
from alignment.alignment_finder import AlignmentFinder
from alignment.loss_function_generators import gradient_optimized_err_lambda, gradient_penalties_lambda
from alignment.alignment_delegate import AlignmentDelegate
from key_reader import KeyReader


alignment_finder = AlignmentFinder(
    gradient_optimized_err_lambda=gradient_optimized_err_lambda,
    gradient_penalties_lambda=gradient_penalties_lambda)

alignment_delegate = AlignmentDelegate(alignment_finder, GLOBALS)


async def main():
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
        (r"/api/alignment", AlignmentHandler,
            dict(globals=GLOBALS,
                alignment_delegate=alignment_delegate)),
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
    logging.info(sys.path)
    logging.info(os.getcwd())
    logging.info("ready")
    await asyncio.Event().wait()


if __name__ == "__main__":
    define("debug", default=False, help="run in debug mode", type=bool)
    parse_command_line()

    asyncio.run(main())
