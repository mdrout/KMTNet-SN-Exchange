import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from datetime import timedelta
import glob,sys


def great_circle_distance(ra1, dec1, ra2, dec2):
    """
    Calculate the great circle distance between two points on the celestial sphere.

    :param ra1: Right Ascension of point 1 (degrees)
    :param dec1: Declination of point 1 (degrees)
    :param ra2: Right Ascension of point 2 (degrees)
    :param dec2: Declination of point 2 (degrees)
    :return: angular separation of the two points (degrees)
    """
    ra1_rad, dec1_rad = np.deg2rad([ra1, dec1])
    ra2_rad, dec2_rad = np.deg2rad([ra2, dec2])
    # Spherical law of cosines
    distance_in_radians = np.sin(dec1_rad) * np.sin(dec2_rad)
    distance_in_radians += np.cos(dec1_rad) * np.cos(dec2_rad) * np.cos(ra2_rad - ra1_rad)
    distance_in_radians = np.arccos(distance_in_radians)
    return np.rad2deg(distance_in_radians)


def coords_from_filename(coords):
    """Create an astropy Coordinate object based on the coordinate string
    which is found in many of the kmtshi file names

    :param coords: input string. Format assumed as: 062448D724-223052D3
    :return: SkyCoord object"""

    ra = coords[0:2] + " " + coords[2:4] + " " + coords[4:6] + "." + coords[7:10]
    dec = coords[10:13] + " " + coords[13:15] + " " + coords[15:17] + "." + coords[18]
    c = SkyCoord(ra + " " + dec, unit=(u.hourangle, u.deg))
    return c


def initialize_duplicates(epoch_prim,dt,epochs_f,epoch_timestamps):
    """This will load up an array with the ra and dec of all of the objects
    That I will want to check against to see if their are multiple detections.
    This saves time to avoid repeated operations unnecessarily.

    :param epoch_prim: Epoch of primary search (datetime object)
    :param dt: number of days previous to primary epoch in which to conduct search
    :param epochs_f: array which contains the folder path to all of the epochs for this field
    :param epoch_timestamps: datetime objects for all of the epochs above

    NB: both epochs_f and epochs_timestamps are arrays created in kmtshi_search that can be passed"""

    day_min = epoch_prim - timedelta(days=dt)
    day_max = epoch_prim
    index = np.where([((epoch < day_max) & (epoch > day_min)) for epoch in epoch_timestamps])[0]
    ra = []
    dec = []

    # Looping this way ensures that data taken most recently before is searched first.
    for j in np.flipud(index):
        events_ch = glob.glob(epochs_f[j] + '/*/*.pdf')

        for event_ch_f in events_ch:
            event_ch_txt = event_ch_f.split('/')[-1].split('.')
            c = coords_from_filename(event_ch_txt[5])
            ra.append(c.ra.deg)
            dec.append(c.dec.deg)

    return ra, dec


def initialize_duplicates_set(epoch_ref,dt,epochs_f,epoch_timestamps):
    """This will load up an array with the ra and dec of all of the objects
    that I could possibly need to check against for a list of epochs for a field.
    It will initialize everything between dt days prior to the earliest epoch
    that is *after* the reference epoch for this field.

    In the main program I will then need to select which subset of members of this array
    I *actually* need to check against. So I now need to output a timestamp
    as well as an ra/dec for each member of this field.

    This will save even more time to avoid repeated operations unnecessarily.

    :param epoch_ref: Epoch of reference date for this epoch. (datetime object)
                    Only need to initialize for dates AFTER this.
    :param dt: number of days previous to primary epoch in which to conduct search
    :param epochs_f: array which contains the folder path to all of the epochs for this field
    :param epoch_timestamps: datetime objects for all of the epochs above

    NB: both epochs_f and epochs_timestamps are arrays created in kmtshi_search that can be passed"""

    # Identify the first epoch in list which is after the reference date:
    day_min = epoch_ref - timedelta(days=dt)
    for epoch_ts in epoch_timestamps:
        if epoch_ts > epoch_ref:
            day_min = epoch_ts - timedelta(days=dt)
            break

    # Set max day to be the final epoch
    day_max = epoch_timestamps[-1]

    index = np.where([((epoch < day_max) and (epoch > day_min)) for epoch in epoch_timestamps])[0]
    ra = []
    dec = []
    times = []

    # Looping this way ensures that data taken most recently before is searched first.
    for j in np.flipud(index):
        events_ch = glob.glob(epochs_f[j] + '/*/*.pdf')

        for event_ch_f in events_ch:
            event_ch_txt = event_ch_f.split('/')[-1].split('.')
            c = coords_from_filename(event_ch_txt[5])
            ra.append(c.ra.deg)
            dec.append(c.dec.deg)
            times.append(epoch_timestamps[j])

    return ra, dec, times