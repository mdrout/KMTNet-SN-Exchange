from astroquery.simbad import Simbad
from astroquery.ned import Ned
from astropy import coordinates
import astropy.units as u
import numpy as np
from kmtshi.coordinates import great_circle_distance

def simbad_query(ra, dec, radius):
    '''Simbad astroquery around a set of coordinates.

    :param ra: Right Ascension of point  (degrees)
    :param dec: Declination of point  (degrees)
    :param radius: Radius around point for cone search (arcsec)
    '''

    # Set-up output columns
    customSimbad = Simbad()
    customSimbad.remove_votable_fields('coordinates')
    customSimbad.add_votable_fields('ra(d;;;;)','dec(d;;;;)','otype(V)','sp', 'rvz_radvel')

    # Create coordinate object
    c = coordinates.SkyCoord(ra, dec, unit='deg')
    r = radius * u.arcsecond
    result_table = customSimbad.query_region(c, radius=r)
    result_table2= np.array(result_table)

    # Calculate the distance between the objects and our coordinates:
    if result_table:
        distance = [great_circle_distance(ra,dec,result_table['RA_d____'][x],result_table['DEC_d____'][x])*3600. for x in range(len(result_table))]
    else:
        distance = 0.

    return result_table,result_table2,distance

def ned_query(ra, dec, radius):
    '''Ned astroquery around a set of coordinates.

    :param ra: Right Ascension of point  (degrees)
    :param dec: Declination of point  (degrees)
    :param radius: Radius around point for cone search (arcsec)
    '''

    # Create coordinate object
    c = coordinates.SkyCoord(ra, dec, unit='deg')
    r = radius * u.arcsecond
    result_table = Ned.query_region(c, radius=r)

    name = result_table['Object Name']
    ra1 = result_table['RA(deg)']
    dec1 = result_table['DEC(deg)']
    distance = result_table['Distance (arcmin)']*60. # Now in arcseconds
    ttype = result_table['Type']
    redshift = result_table['Redshift']

    if result_table:
        result_table2 = sorted(zip(distance,name,ra1,dec1,ttype,redshift))
    else:
        result_table2 = result_table

    return result_table,result_table2