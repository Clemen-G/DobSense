import math
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy import units as u
from astropy.time import Time
from alignment.utils import rot, deg, r, X, Y, Z

def eq_to_alt_az(eq_coordinates_str, location, timestamp):
    """Converts RA/DEC coordinates to alt-az for a given location/time

    Args:
        eq_coordinates_str: str "00 08 23.17 +29 05 27.0" hh mm ss deg min sec
        location: {"altitude":342.36, "latitude":42.6, "longitude":13.693}
        timestamp: unix_epoch in seconds

    Returns:
        A SkyCoords object whose .az.value and .alt.value represent the alt/az
        coordinates in degrees.
    """
    # see https://docs.astropy.org/en/stable/coordinates/
    obj_radec = SkyCoord(eq_coordinates_str, unit=(u.hourangle, u.deg))
    time = Time(val=timestamp, format='unix')
    curr_location = EarthLocation(lat=location["latitude"]*u.deg,
                                  lon=location["longitude"]*u.deg,
                                  height=location["altitude"]*u.m)
    alt_az = obj_radec.transform_to(AltAz(obstime=time,
                                    location=curr_location))
    return alt_az


def taz_to_az(alignment_matrices, taz, talt):
    """Returns the alt-az coordinates of an object at given taz, talt

    Arguments:
        alignment_matrices: named tuple containing R_azO, R_altO, R_tilt
        taz: telescope azimuth in deg
        talt: telescope altitude in deg

    Returns:
        a dict {"az": 123, "alt": 12} with angles in degrees
    """

    az_vector = (alignment_matrices.R_azO.T @
              rot(Z, r(-taz)) @
              alignment_matrices.R_tilt.T @
              alignment_matrices.R_altO.T @
              rot(Y, r(-talt)) @ X)

    az = math.atan2(az_vector[1], az_vector[0])
    alt = math.atan2(az_vector[2],
                     math.sqrt(
                         math.pow(az_vector[0], 2) + math.pow(az_vector[1], 2)))

    return {"az": deg(az), "alt": deg(alt)}