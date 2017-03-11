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

            print('Time for cycle through initialize list: ',time.clock()-t_circle)
            print('Time for a single catalog file ',time.clock()-start)
            break
        #print number of points in database for this filter
        #n1=Photometry.objects.filter(candidate=c1).filter(filter=filter).count()
        #print(filter+' points present = '+str(n1))

    out_txt = 'Photometry has been updated for Object '+str(c1.name)
    return out_txt


def cphotom_list_t(candidate_ids):
    '''This calclates timing for a list of inputs.'''

    # #######################################################################
    # Check that all of the candidate_ids have same sub-field and quadrant.
    flds = [Candidate.objects.get(pk=x).field.subfield for x in candidate_ids]
    quads = [Candidate.objects.get(pk=x).quadrant.name for x in candidate_ids]
    if len(set(flds)) > 1:
        print('Not all candidates for photom are in same fld')
        sys.exit()
    elif len(set(quads)) > 1:
        print('Not all candidates for photom are in same quadrant')
        sys.exit()

    # If pass test, initialize one so field and quandrant can be called:
    c1 = Candidate.objects.get(pk=candidate_ids[0])

    # ###################################################################
    # Set-up places to searh:
    filters = ['V','I','Bsub']
    base = base_foxtrot() + base_data() + c1.field.name + '/' + c1.field.subfield + '/' + c1.quadrant.name + '/'

    time_filter = time.clock()
    # Cycle through filters:
    for filter in filters:

        # ########################################################################
        # Initialize a list of reference timestamps for all of the input candidates.
        # This is done on a filter-by-filter basis
        # This is a test, so all set to 2014, but want to mimic process:

        timestamps_ref = []
        for y in range(0, len(candidate_ids)):
            timestamps_ref.append(datetime.datetime(2014, 1, 1, 00, 00, tzinfo=timezone.utc))


        files = glob.glob(base + '*.' + filter + '.*_tan.nh.phot.cat')

        # Cycle through catalog files
        for file in files:
            print(file)
            start = time.clock()

            # basic splitting:
            t2 = file.split('/')[-1].split('.')

            # determine date from filename:
            timestamp = dates_from_filename('20' + t2[3])

            # Make a list of pks for candidates need to be checked for this epoch.
            index = np.where([(timestamp_ref < timestamp) for timestamp_ref in timestamps_ref])
            candidates_to_check = [candidate_ids[x] for x in index[0]]  # list of pks.

            # If there are no candidates in list that need to be checked
            # for this epoch, move on.
            if not len(candidates_to_check) > 0:
                continue

            # initialize list of ras and decs for the cases that need to be checked.
            start_cand = time.clock()
            ctc_ra = [Candidate.objects.get(pk=w).ra for w in candidates_to_check]
            ctc_dec = [Candidate.objects.get(pk=w).dec for w in candidates_to_check]
            print('Time to innitialize candidate ra/dec ',time.clock()-start_cand)

            # open the catalog file, and initialize the ra/dec for objects inside.
            hdulist = fits.open(file)
            start_t = time.clock()
            ra_cat = [event['X_WORLD'] for event in hdulist[2].data]
            dec_cat = [event['Y_WORLD'] for event in hdulist[2].data]
            print('Time for initialization of ',t2[3],' ',filter,' catalog ra/dec: ', time.clock() - start_t)

            # Now loop over the candidates which need to be check to find matches:
            start_loop = time.clock()
            for j in range(0, len(candidates_to_check)):
                c1 = Candidate.objects.get(pk=candidates_to_check[j])
                Flag = False  # tracker for whether we have a match at this epoch.

                # Loop over the catalog events:
                start_sloop = time.clock()
                for i in range(0, len(ra_cat)):

                    if great_circle_distance(ctc_ra[j], ctc_dec[j], ra_cat[i], dec_cat[i]) < (1.0 / 3600.0):
                        event = hdulist[2].data[i]

                        if event['FLUX_AUTO'] <= 0.0:
                            continue  # Tell it to just move on.
                        if event['FLUX_APER'] <= 0.0:
                            continue


                        # If condition is met, then consider object to be the same:
                        # Grab photom info. Update database. Set the flag. Break from event loop (move to next file).
                        photom_obj = Photometry(candidate=c1, obs_date=timestamp, filter=filter, telescope=t2[4],
                                                flag=True)

                        t = Time(timestamp)
                        photom_obj.obs_mjd = t.mjd

                        photom_obj.ra = event['X_WORLD']
                        photom_obj.dec = event['Y_WORLD']
                        if np.isnan(event['ERRA_WORLD']):
                            photom_obj.dra = 0.0
                        else:
                            photom_obj.dra = event['ERRA_WORLD']
                        if np.isnan(event['ERRB_WORLD']):
                            photom_obj.ddec = 0.0
                        else:
                            photom_obj.ddec = event['ERRB_WORLD']
                        if np.isnan(event[CLASS_STAR]):
                            photom_obj.class_star = 99.999
                        else:
                            photom_obj.class_star = event['CLASS_STAR']

                        # Sort out the photometry:
                        photom_obj.flux_ap = event['FLUX_APER']
                        photom_obj.dflux_ap = event['FLUXERR_APER']
                        photom_obj.flux_auto = event['FLUX_AUTO']
                        photom_obj.dflux_auto = event['FLUXERR_AUTO']
                        photom_obj.mag_auto = event['MAG_AUTO']

                        # calculate the other magnitudes/errors from this information.
                        # mag = -2.5*alog10(F)+zpt
                        # dmag = 2.5 dF/(ln(10)*F)
                        zpt = event['MAG_AUTO'] + 2.5 * np.log10(event['FLUX_AUTO'])
                        dmag_auto = 2.5 * event['FLUXERR_AUTO'] / (np.log(10) * event['FLUX_AUTO'])
                        mag_ap = -2.5 * np.log10(event['FLUX_APER']) + zpt
                        dmag_ap = 2.5 * event['FLUXERR_APER'] / (np.log(10) * event['FLUX_APER'])

                        photom_obj.dmag_auto = dmag_auto
                        photom_obj.mag_ap = mag_ap
                        photom_obj.dmag_ap = dmag_ap

                        photom_obj.save()
                        Flag = True
                        break  # This moves onto the next candidate_to_check

                # Add a 'default entry if no match was found. To show that data was taken that day.
                if not Flag:
                    # This indicates that there was no match, so populated with defaults.
                    photom_obj = Photometry(candidate=c1, obs_date=timestamp, filter=filter, telescope=t2[4],
                                            flag=False,
                                            ra=0.00, dec=0.00, dra=0.00, ddec=0.00, class_star=0.00, flux_ap=0.00,
                                            dflux_ap=0.00,
                                            flux_auto=0.00, dflux_auto=0.00, mag_auto=22.0, dmag_auto=0.00, mag_ap=22.0,
                                            dmag_ap=0.00)

                    t = Time(timestamp)
                    photom_obj.obs_mjd = t.mjd
                    photom_obj.save()
                # print('Time for loop over single candidate object ',time.clock()-start_sloop)
            # Finished searching candidates for this epoch can close cat file.
            hdulist.close()
            print('Time to cross check ',len(candidates_to_check),' = ',time.clock()-start_loop)
            print('Time for single catalog file: ',time.clock()-start)
            #break
        print('Time for filter ',time.clock()-time_filter)

    out_txt = 'Photometry has been updated for list of events'
    return out_txt