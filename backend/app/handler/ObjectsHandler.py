from .AppHandler import AppHandler


class ObjectsHandler(AppHandler):
    def get(self):
        self.set_header('Content-Encoding', 'gzip')
        self.write(self.globals.catalogs.objects)