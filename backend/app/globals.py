import os
import json
from data_model import AlignmentPoints


class SystemState:
    def __init__(self):
        self._alignment_points = AlignmentPoints()
        self._alignment_matrices = None
        self._location = None

    @property
    def alignment_matrices(self):
        return self._alignment_matrices
    
    @alignment_matrices.setter
    def alignment_matrices(self, value):
        self._alignment_matrices = value

    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, value):
        if self._location is not None:
            raise ValueError("Location can be set only once")
        self._location = value
    
    @property
    def alignment_points(self):
        return self._alignment_points


class Catalogs:
    def __init__(self) -> None:
        self._load_constellation_data()

    @property
    def constellations(self):
        return self._constellations_stars

    def get_star_info(self, star_id):
        return self._stars[star_id]

    def _load_constellation_data(self):
        mod_path = os.path.dirname(os.path.realpath(__file__))
        with open(mod_path + "/../data/constellations_stars.json") as f:
            self._constellations_stars = json.load(f)

        self._stars = {
            obj["HIP"]: obj
                for const in self._constellations_stars
                    for obj in const["stars"]}


class Globals:
    def __init__(self):
        self.state = SystemState()
        self.catalogs = Catalogs()


GLOBALS = Globals()
