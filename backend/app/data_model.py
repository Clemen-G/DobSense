from pydantic import BaseModel, ConfigDict, Field
from typing import List


class AltAzCoords(BaseModel):
    model_config = ConfigDict(frozen=True)
    az: float
    alt: float


class TazCoords(BaseModel):
    model_config = ConfigDict(frozen=True)
    taz: float
    talt: float


class EqCoords(BaseModel):
    model_config = ConfigDict(frozen=True)
    ra: float
    dec: float


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


# this message is client-generated and is kept here
# only for protocol visibility
class Hello(BaseModel):
    model_config = ConfigDict(frozen=True)
    messageType: str = Field(default="Hello",
                             init_var=False)


class IsAligned(BaseModel):
    model_config = ConfigDict(frozen=True)
    isTelescopeAligned: bool
    messageType: str = Field(default="IsAligned",
                             init_var=False)


class TelescopeCoords(BaseModel):
    model_config = ConfigDict(frozen=True)
    taz_coords: TazCoords
    alt_az_coords: AltAzCoords
    eq_coords: EqCoords
    messageType: str = Field(default="TelescopeCoords",
                             init_var=False)


class TargetCoords(BaseModel):
    model_config = ConfigDict(frozen=True)
    object_id: str
    taz_coords: TazCoords
    alt_az_coords: AltAzCoords
    eq_coords: EqCoords
    messageType: str = Field(default="TargetCoords",
                             init_var=False)
