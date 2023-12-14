from enum import Enum
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


class AlignmentPointState(str, Enum):
    CANDIDATE = "candidate"
    EFFECTIVE = "effective"
    DELETING = "deleting"


class AlignmentPoint(BaseModel):
    model_config = ConfigDict(frozen=True)
    # currently, hipparcos id
    object_id: int
    timestamp: float
    # this alignment's id
    id: str
    taz_coords: TazCoords
    alt_az_coords: AltAzCoords
    state: AlignmentPointState = Field(default=AlignmentPointState.CANDIDATE)
    messageType: str = Field(default="AlignmentPoint",
                             init_var=False)

    # clones this object changing only its state
    def clone_with_state(self, state: AlignmentPointState):
        return self.model_copy(update={"state": state})


# required for serialization to provide a messageType
class AlignmentPointsMessage(BaseModel):
    model_config = ConfigDict(frozen=True)
    alignment_points: List[AlignmentPoint]
    messageType: str = Field(default="AlignmentPointsMessage",
                             init_var=False)

# this message is client-generated and is kept here
# only for protocol visibility
class Hello(BaseModel):
    model_config = ConfigDict(frozen=True)
    messageType: str = Field(default="Hello",
                             init_var=False)


class IsAlignedMessage(BaseModel):
    model_config = ConfigDict(frozen=True)
    isTelescopeAligned: bool
    messageType: str = Field(default="IsAlignedMessage",
                             init_var=False)


class TelescopeCoords(BaseModel):
    model_config = ConfigDict(frozen=True)
    taz_coords: TazCoords
    alt_az_coords: AltAzCoords
    eq_coords: EqCoords


class TelescopeCoordsMessage(BaseModel):
    model_config = ConfigDict(frozen=True)
    telescope_coords: TelescopeCoords
    messageType: str = Field(default="TelescopeCoordsMessage",
                             init_var=False)


class TargetCoords(BaseModel):
    model_config = ConfigDict(frozen=True)
    object_id: str
    taz_coords: TazCoords
    alt_az_coords: AltAzCoords
    eq_coords: EqCoords


class TargetCoordsMessage(BaseModel):
    model_config = ConfigDict(frozen=True)
    target_coords: TargetCoords
    messageType: str = Field(default="TargetCoordsMessage",
                             init_var=False)
