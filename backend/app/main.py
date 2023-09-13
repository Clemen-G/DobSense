import os
import sys
import logging
import asyncio
import json
import tornado
from handlers import HandshakeHandler, AlignmentHandler, AlignmentsHandler
from handlers import RealTimeMessagesWebSocket
from tornado.options import define, options, parse_command_line
from alignment.telescope_interface import TelescopeInterface, generate_matrices
from alignment.alignment_finder import AlignmentFinder
from alignment.loss_function_generators import gradient_optimized_err_lambda, gradient_penalties_lambda
from alignment.alignment_delegate import AlignmentDelegate
from data_model import AlignmentPoints
from key_reader import KeyReader


GLOBALS = {
    "location": None,
    #  [{'object_id': 54061,
    # 'timestamp': 1694338900.363,
    # 'id': '6a7c26fe-c9a3-46fc-a819-a717b6486b90',
    # 'taz_coords': {'taz': 13.32155705976877, 'talt': 38.21793978375107},
    # 'alt_az_coords': {'az': 23.321557059768754, 'alt': 68.21793978375106}}]
    "alignment_points": AlignmentPoints(),
    "constellation_data": None,
    "stars": None,
    "app_path": os.path.dirname(os.path.realpath(__file__)),
    "alignment_matrices": None,
}

hyperparameters = {
    "num_steps": 200,
    "alpha": .4,
    "beta": .85,
    "penalty_weight": 1,
    "n_samples_correction": True,
}
alignment_finder = AlignmentFinder(
    gradient_optimized_err_lambda=gradient_optimized_err_lambda,
    gradient_penalties_lambda=gradient_penalties_lambda,
    hyperparameters=hyperparameters)

alignment_delegate = AlignmentDelegate(alignment_finder, GLOBALS)


async def main():
    key_reader = KeyReader()
    telescope_interface = TelescopeInterface(
        alignment_matrices=generate_matrices(),
        key_reader=key_reader)
    
    application = tornado.web.Application([
        (r"/api/handshake", HandshakeHandler, dict(globals=GLOBALS)),
        (r"/api/alignments",
         AlignmentsHandler,
         dict(globals=GLOBALS,
              telescope_interface=telescope_interface)),
        (r"/api/alignment", AlignmentHandler,
         dict(
            globals=GLOBALS,
            alignment_delegate=alignment_delegate)),
        (r"/api/websocket", RealTimeMessagesWebSocket,
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
