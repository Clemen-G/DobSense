from pydantic import BaseModel, ConfigDict, TypeAdapter
from typing import List


class AltAzCoords(BaseModel):
    model_config = ConfigDict(frozen=True)
    az: float
    alt: float


class TazCoords(BaseModel):
    model_config = ConfigDict(frozen=True)
    taz: float
    talt: float


class AlignmentPoint(BaseModel):
    model_config = ConfigDict(frozen=True)
    # currently, hipparcos id
    object_id: int
    timestamp: float
    # this alignment's id
    id: str
    taz_coords: TazCoords
    alt_az_coords: AltAzCoords


class AlignmentPoints(BaseModel):
    alignment_points: List[AlignmentPoint] = []
