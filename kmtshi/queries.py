from astroquery.simbad import Simbad
from astropy import coordinates
import astropy.units as u
import numpy as np

def simbad_query(ra, dec, radius):
    '''Simbad astroquery around a set of coordinates.

    :param ra: Right Ascension of point  (degrees)
    :param dec: Declination of point  (degrees)
    :param radius: Radius around point for cone search (arcsec)
    '''

    # Set-up output columns
    customSimbad = Simbad()
    customSimbad.remove_votable_fields('coordinates')
    customSimbad.add_votable_fields('ra(:;;;;)','dec(:;;;;)','otype(V)','sp', 'rvz_radvel')

    # Create coordinate object
    c = coordinates.SkyCoord(ra, dec, unit='deg')
    r = radius * u.arcsecond
    result_table = customSimbad.query_region(c, radius=r)
    result_table2= np.array(result_table)

    return result_table,result_table2
