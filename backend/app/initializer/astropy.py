import logging
from astropy.utils import iers


def set_astropy_offline():
    iers.conf.iers_degraded_accuracy = 'ignore'
    iers.conf.iers_auto_url = 'file:///persistent_folder/iers.txt'
    iers.conf.iers_auto_url_mirror = ''
    iers.conf.iers_leap_second_auto_url = 'file:///persistent_folder/leap-seconds.list'
    iers.conf.ietf_leap_second_auto_url = ''