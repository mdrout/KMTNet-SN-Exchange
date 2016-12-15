import numpy as np


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
