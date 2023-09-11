import numpy as np
from http import HTTPStatus
from threading import Lock, Thread

from alignment.utils import get_unit_vector, r
from exceptions import UserException


class AlignmentDelegate:
    def __init__(self, alignment_finder) -> None:
        self.provided_coordinates = None
        self.lock = Lock()
        self.alignment_finder = alignment_finder

    def start_alignment_procedure(self, alignment_points):
        self._set_current_coordinates(alignment_points)

        t = Thread(target=self.align,
                   name="alignment_procedure_thread",
                   kwargs={"coordinates": self.provided_coordinates})
        t.start()

    def align(self, coordinates):
        res = self.alignment_finder.get_alignment_matrices(coordinates)
        self.provided_coordinates = None

        print(res)

    def _set_current_coordinates(self, alignment_points):
        alignment_points = [[
                -p['taz_coords']['taz'],
                -p['taz_coords']['talt'],
                p['alt_az_coords']['az'],
                p['alt_az_coords']['alt']]
                for p in alignment_points]
        alignment_points = np.array(alignment_points)
        taz_co_sines = np.hstack((
            (np.cos(r(alignment_points[:, 0:2])),
             np.sin(r(alignment_points[:, 0:2])))))
        # taz_co_sines format: cos taz, sin taz, cos talt, sin talt
        taz_co_sines[:, [2, 1]] = taz_co_sines[:, [1, 2]]
        az_unit_vectors = np.array(
            [np.squeeze(get_unit_vector(az, alt))
                for (az, alt) in alignment_points[:, 2:]])
        current_coordinates = np.hstack((taz_co_sines, az_unit_vectors))
        with self.lock:
            if self.provided_coordinates is not None:
                raise UserException(http_code=HTTPStatus.CONFLICT,
                    user_message="Another alignment is currently running")
            self.provided_coordinates = current_coordinates