'''This is a routine that can be called in order to either initialize
or update the photometry for a given candidate. This one I will specifically
work to optimize the timing.  Want to test methods for a single catalog file'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")

#continue on to rest:
import django
django.setup()
from django.utils import timezone

from kmtshi.models import Candidate,Photometry,Field,Quadrant
from kmtshi.dates import dates_from_filename
from kmtshi.coordinates import great_circle_distance
from kmtshi.base_directories import base_data,base_foxtrot
from astropy.io import fits
from astropy.time import Time
import datetime,glob,time
import numpy as np


def cphotom_t(candidate_id):
    '''This will find the photometry for a specific candidate'''
    c1 = Candidate.objects.get(pk=candidate_id)
    c1_ra = c1.ra
    c1_dec = c1.dec

    #Define ref time to search based on info in the Photom database already.

    timestamp_ref = datetime.datetime(2014,1,1,00,00,tzinfo=timezone.utc)

    ####################################################################
    #Set-up places to searh:
    filters = ['B']
    base = base_foxtrot()+base_data()+c1.field.name+'/'+c1.field.subfield+'/'+c1.quadrant.name+'/'

    #Cycle through filters:
    for filter in filters:
        files = glob.glob(base + '*.' + filter + '.*_tan.nh.phot.cat')

        #Cycle through catalog files
        for file in files:
            print(file)
            start = time.clock()

            #basic splitting:
            t2 = file.split('/')[-1].split('.')
            t3 = t2[3]

            # determine date from filename:
            timestamp = dates_from_filename('20'+t3)

            #decide if I need to look at this file based on reference date;
            #if not after reference date, then move on to next file
            if not (timestamp > timestamp_ref):
                continue

            #open file:
            topen = time.clock()
            hdulist = fits.open(file)
            print('time to open file = ', time.clock()-topen)
            #check the ra/dec of objects against candidate:
            #NB: Currently just takes FIRST object w/in 1". Not good for crowded fields...

            Flag = False #trackker for whether we have a match at this epoch.
            start_t = time.clock()
            ra_cat = [event['X_WORLD'] for event in hdulist[2].data]
            dec_cat = [event['Y_WORLD'] for event in hdulist[2].data]
            print('Time for initialization of ra/dec: ',time.clock()-start_t)

            t_circle = time.clock()
            #for event in hdulist[2].data:
            for i in range(0,len(ra_cat)):

                #if great_circle_distance(c1_ra, c1_dec, event['X_WORLD'], event['Y_WORLD']) < (1.0 / 3600.0):
                if great_circle_distance(c1_ra, c1_dec, ra_cat[i], dec_cat[i]) < (1.0 / 3600.0):

                    event = hdulist[2].data[i]
                    #If condition is met, then consider object to be the same:
                    #Grab photom info. Update the database. Set the flag. Break from event loop (move to next file).
                    photom_obj = Photometry(candidate=c1,obs_date=timestamp,filter=filter,telescope=t2[4],flag=True)

                    t=Time(timestamp)
                    photom_obj.obs_mjd=t.mjd

                    photom_obj.ra = event['X_WORLD']
                    photom_obj.dec = event['Y_WORLD']
                    photom_obj.dra = event['ERRA_WORLD']
                    photom_obj.ddec = event['ERRB_WORLD']
                    photom_obj.class_star = event['CLASS_STAR']

                    #Sort out the photometry:
                    photom_obj.flux_ap = event['FLUX_APER']
                    photom_obj.dflux_ap = event['FLUXERR_APER']
                    photom_obj.flux_auto = event['FLUX_AUTO']
                    photom_obj.dflux_auto = event['FLUXERR_AUTO']
                    photom_obj.mag_auto = event['MAG_AUTO']

                    #calculate the other magnitudes/errors from this information.
                    #mag = -2.5*alog10(F)+zpt
                    #dmag = 2.5 dF/(ln(10)*F)
                    zpt = event['MAG_AUTO'] + 2.5 * np.log10(event['FLUX_AUTO'])
                    dmag_auto = 2.5*event['FLUXERR_AUTO']/(np.log(10)*event['FLUX_AUTO'])
                    mag_ap = -2.5*np.log10(event['FLUX_APER']) + zpt
                    dmag_ap = 2.5*event['FLUXERR_APER']/(np.log(10)*event['FLUX_APER'])
                    hdulist.close()

                    photom_obj.dmag_auto = dmag_auto
                    photom_obj.mag_ap = mag_ap
                    photom_obj.dmag_ap = dmag_ap

                    #photom_obj.save()
                    Flag = True
                    break

            #Add a 'default entry if no match was found. To show that data was taken that day.
            if not Flag:

                #This indicates that there was no match, so populated with defaults.
                photom_obj = Photometry(candidate=c1, obs_date=timestamp, filter=filter, telescope=t2[4], flag=False,
                                        ra=0.00,dec=0.00,dra=0.00,ddec=0.00,class_star=0.00,flux_ap=0.00,dflux_ap=0.00,
                                        flux_auto=0.00,dflux_auto = 0.00,mag_auto = 22.0,dmag_auto=0.00,mag_ap = 22.0,
                                        dmag_ap = 0.00)

                t = Time(timestamp)
                photom_obj.obs_mjd = t.mjd
                #photom_obj.save()

            print('Time for cycle through initialize list: ',time.close()-t_circle)
            print('Time for a single catalog file ',time.clock()-start)
            break
        #print number of points in database for this filter
        #n1=Photometry.objects.filter(candidate=c1).filter(filter=filter).count()
        #print(filter+' points present = '+str(n1))

    out_txt = 'Photometry has been updated for Object '+str(c1.name)
    return out_txt
