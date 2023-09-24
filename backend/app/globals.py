import os
import json
import logging
from data_model import AlignmentPoints


class SystemState:
    ALIGN_CHANGE = "ALIGN_CHANGE"
    events = set([ALIGN_CHANGE])

    def __init__(self):
        self._alignment_points = AlignmentPoints()
        self._alignment_matrices = None
        self._location = None
        self._event_listeners = {e: set() for e in self.__class__.events}

    @property
    def alignment_matrices(self):
        return self._alignment_matrices
    
    @alignment_matrices.setter
    def alignment_matrices(self, value):
        self._alignment_matrices = value
        self._notify_listeners(self.__class__.ALIGN_CHANGE)

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

    def register(self, event_name, handler):
        if event_name not in self.__class__.events:
            raise ValueError("unknown event " + event_name)
        if handler in self._event_listeners[event_name]:
            raise ValueError("handler already registered for this event")
        self._event_listeners[event_name].add(handler)
    
    def unregister(self, event_name, handler):
        if event_name not in self.__class__.events:
            raise ValueError("unknown event " + event_name)
        if handler not in self._event_listeners[event_name]:
            raise ValueError("handler not registered for this event")
        self._event_listeners[event_name].remove(handler)
    
    def _notify_listeners(self, event_name):
        for listener in self._event_listeners[event_name]:
            listener(event_name)


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
