import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord

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

def coords_from_filename(filestring):
    '''Create an astropy Coordinate object based on the coordinate string
    which is found in many of the kmtshi file names

    :param filestring: input string. Format assumed as: 062448D724-223052D3
    :return: SkyCoord object'''

    ra = coords[0:2] + " " + coords[2:4] + " " + coords[4:6] + "." + coords[7:10]
    dec = coords[10:13] + " " + coords[13:15] + " " + coords[15:17] + "." + coords[18]
    c = SkyCoord(ra + " " + dec, unit=(u.hourangle, u.deg))
    return c
