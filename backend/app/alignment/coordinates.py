from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy import units as u
from astropy.time import Time


def eq_to_alt_az(eq_coordinates_str, location, timestamp):
    """Converts RA/DEC coordinates to alt-az for a given location/time

    Args:
        eq_coordinates_str: str "00 08 23.17 +29 05 27.0" hh mm ss deg min sec
        location: {"altitude":342.36, "latitude":42.6, "longitude":13.693}
        timestamp: unix_epoch

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
