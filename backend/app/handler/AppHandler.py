import tornado
from exceptions import UserException


class AppHandler(tornado.web.RequestHandler):
    def initialize(self, globals):
        self.globals = globals

    # https://stackoverflow.com/questions/35254742/tornado-server-enable-cors-requests
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:8000")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

    def write_error(self, status_code, **kwargs):
        # kwargs: {'exc_info': 
        #    (<class 'exceptions.UserException'>,
        #    UserException(UserException(...), 'Alignment requires at least 3 distinct objects'),
        #    <traceback object at 0x7fb91e766940>)}

        if kwargs['exc_info'][0] == UserException:
            self.set_status(409)
            message = str(kwargs['exc_info'][1].user_message)
            self.write({"error_message": message})
            self.finish()