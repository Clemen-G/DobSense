from exceptions import UserException
from .AppHandler import AppHandler


class AlignmentHandler(AppHandler):
    def initialize(self, globals, alignment_delegate):
        self.alignment_delegate = alignment_delegate
        return super().initialize(globals)

    def post(self):
        alignment_points = self.globals.state.alignment_points.get_candidates()
        self._validate_get_input(alignment_points)
        self.alignment_delegate.start_alignment_procedure(alignment_points,
                                                          synchronous=True)
        self.set_status(200)
        self.finish()

    def _validate_get_input(self, alignment_points):
        if len(set((p.object_id for p in alignment_points))) < 3:
            raise UserException(http_code=400,
                                user_message="Alignment requires at least 3 distinct objects")