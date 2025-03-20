import os
import json
import gzip
import time
import logging
from data_model import EqCoords, AlignmentPoint, AlignmentPointState


logger = logging.getLogger(__name__)


class SystemState:
    ALIGN_CHANGE = "ALIGN_CHANGE"
    TARGET_CHANGE = "TARGET_CHANGE"
    ALIGNMENT_POINTS_CHANGE = "ALIGNMENT_POINTS_CHANGE"
    events = set([ALIGN_CHANGE, TARGET_CHANGE, ALIGNMENT_POINTS_CHANGE])

    def __init__(self):
        self._alignment_matrices = None
        self._location = None
        self._target = None
        self._time_offset = None
        self._alignment_points = AlignmentPoints(self._alignment_points_change)
        self._event_listeners = {e: set() for e in self.__class__.events}

    @property
    def alignment_matrices(self):
        return self._alignment_matrices
    
    @alignment_matrices.setter
    def alignment_matrices(self, value):
        self._alignment_matrices = value
        self.alignment_points.alignment_update()
        self._notify_listeners(self.__class__.ALIGN_CHANGE)

    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, value):
        if self._location is not None:
            return
        self._location = value
    
    @property
    def alignment_points(self):
        return self._alignment_points

    @property
    def target(self):
        return self._target
    
    @target.setter
    def target(self, object_id):
        self._target = object_id
        self._notify_listeners(self.__class__.TARGET_CHANGE)

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
    
    @property
    def time(self):
        if not self._time_offset:
            return None
        else:
            return time.time() + self._time_offset
    
    @time.setter
    def time(self, t0):
        if self._time_offset:
            return
        # t - t_rasp = t0 - t0_rasp
        self._time_offset = t0 - time.time()
        logger.info("time offset set to " + str(self._time_offset))
    
    def _notify_listeners(self, event_name):
        for listener in self._event_listeners[event_name]:
            listener(event_name)
    
    def _alignment_points_change(self):
        self._notify_listeners(self.__class__.ALIGNMENT_POINTS_CHANGE)


class Catalogs:
    def __init__(self) -> None:
        self._load_constellation_data()
        self._load_saguaro_objects()

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

    def _load_saguaro_objects(self):
        mod_path = os.path.dirname(os.path.realpath(__file__))
        with open(mod_path + '/../data/saguaro_objects.json.gz', 'rb') as f:
            self._saguaro_objects_blob = f.read()

        saguaro_objects = json.loads(
            gzip.decompress(self._saguaro_objects_blob).decode("utf-8"))

        self._saguaro_objects_coords = {o["object_id"]: EqCoords(ra=o["ra"], dec=o["dec"])
            for o in saguaro_objects}

    @property
    def objects(self):
        return self._saguaro_objects_blob
    
    def get_object_coords(self, object_id):
        return self._saguaro_objects_coords.get(object_id, None)


class Globals:
    def __init__(self):
        self.state = SystemState()
        self.catalogs = Catalogs()


class AlignmentPoints():
    def __init__(self, on_change) -> None:
        self.alignment_points  = dict()
        self.on_change = on_change
    
    def add(self, alignment_point: AlignmentPoint):
        if alignment_point.state != AlignmentPointState.CANDIDATE:
            raise ValueError("alignment point state must be CANDIDATE")
        if alignment_point.id in self.alignment_points:
            raise ValueError("duplicate alignment point id")
        self.alignment_points[alignment_point.id] = alignment_point
        self._notify_change()

    def delete(self, alignment_point_id: str):
        if alignment_point_id not in self.alignment_points:
            return
        alignment_point = self.alignment_points[alignment_point_id]
        if alignment_point.state == AlignmentPointState.CANDIDATE:
            del self.alignment_points[alignment_point_id]
        else:
            self.alignment_points[alignment_point_id] = \
                alignment_point.clone_with_state(AlignmentPointState.DELETING)
        self._notify_change()

    def alignment_update(self):
        new_alignment_points = dict()
        for alignment_point in self.alignment_points.values():
            if alignment_point.state == AlignmentPointState.DELETING:
                continue
            new_alignment_points[alignment_point.id] = \
                alignment_point.clone_with_state(AlignmentPointState.EFFECTIVE)
        self.alignment_points = new_alignment_points
        self._notify_change()
    
    def get_candidates(self):
        return [ap for ap in self.alignment_points.values()
            if ap.state != AlignmentPointState.DELETING]
    
    def get_all(self):
        return self.alignment_points.values()

    def _notify_change(self):
        self.on_change()

GLOBALS = Globals()
