import logging
import threading
from astropy.utils import iers
from alignment import coordinates

logger = logging.getLogger(__name__)


def warmup_astropy():
    logger.info("Warming up astropy")
    # hardcoding a timestamp to avoid warnings while the system has not got
    # the current time from a phone
    at_time = "1741703211"
    coordinates.alt_az_to_eq(
            0, 0, {"latitude": 0, "longitude": 0, "altitude": 0}, at_time)
    logger.info("Warm-up completed")


def initialize():
    logging.info("Configuring astropy to rely on local IERS files, if available")
    iers.conf.iers_degraded_accuracy = 'ignore'
    iers.conf.iers_auto_url = 'file:///shared/astropy/finals2000A.all'
    iers.conf.iers_auto_url_mirror = ''
    iers.conf.iers_leap_second_auto_url = 'file:///shared/astropy/leap-seconds.list'
    iers.conf.ietf_leap_second_auto_url = ''
    
    # not 100% sure astropy is thread-safe, but in practice the user
    # will align long after the warmup is done.
    thread = threading.Thread(target=warmup_astropy)
    thread.start()