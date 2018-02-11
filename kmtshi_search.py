'''Basic file which will be called to search a kmtnet field for new transients
This version will call the LC function on all the new candidates within a certain
field and quadrant together, to avoid multiple reads of the same catalog files.'''

#Django set-up:
import getopt
import os
import subprocess
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

#kmtshi set-up:
from kmtshi.models import Field,Quadrant,Classification,Candidate
from kmtshi.base_directories import base_foxtrot,base_gdrive,jpeg_path
from kmtshi.dates import dates_from_filename
from kmtshi.coordinates import great_circle_distance,initialize_duplicates_set
from kmtshi.kmtshi_jpeg import cjpeg_list
from kmtshi.kmtshi_photom import cphotom_list
from kmtshi.alphabet import num2alpha

#Other set-up
import glob,time
import numpy as np
from datetime import timedelta

###################################################################################
def main(argv):
    flds = [] #fields to search
    nd = 3  #number of detections
    dt = 10 #time in days for search
    try:
        opts, args = getopt.getopt(argv,"f:d:t:",["fields=","detect=","days="])
    except getopt.GetoptError:
        print('kmtshi_search.py -f <[list of subfields]> (-d <required # detections> -t <# days for detections>)')
        print('--fields --detect --days are also permitted')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-f","--fields"):
            flds = arg
        elif opt in ("-d","--detect"):
            nd = arg
        elif opt in ("-t","--days"):
            dt = arg
    if len(flds) < 1:
        print('At least one field to search must be specified')
        print('kmtshi_search.py -f <[list of subfields]> (-d <required # detections> -t <# days for detections>)')
        sys.exit(2)
    else:
        if flds == 'all':
            fld_paths = glob.glob(base_gdrive()+'/*-1')+glob.glob(base_gdrive()+'/*-2')+glob.glob(base_gdrive()+'/*-9')
            flds = [f.split('/')[-1] for f in fld_paths]
            print('fields ', flds, ' will be searched')
            print(nd, ' detections within ', dt, ' days will be required')
        else:
            # Sort fields into strings:
            flds_st = str(flds[1:len(flds)-1])
            flds = flds_st.split(',')
            print('fields ',flds,' will be searched')
            print(nd,' detections within ',dt,' days will be required')

    # Set up list of quads:
    quads_all = ['Q0','Q1','Q2','Q3']

    #We are now armed with the proper fields etc.  Continue to do actual search:
    #Step 1: For a given subfield, identify the gdrive folders:
    for fld in flds:
        s1 = Field.objects.get(subfield=fld)
        new_cands = [] #will trace pk of any new objects added, so we can run photometry for all at the end.

        #get database field for use:
        fld_db = Field.objects.get(subfield=fld)
        epoch_ref = fld_db.last_date

        #Grab files for epochs.
        epochs = glob.glob(base_foxtrot()+base_gdrive()+fld+'/*.*')

        #In order to facilitate checking for multiple detections,within a timeframe:
        #I need to select epochs that are within that timeframe before given epoch.
        epoch_timestamps = [dates_from_filename('20'+epoch_f.split('/')[-1].split('.')[0]) for epoch_f in epochs]

        #Initialize comparison ra/dec for duplicate search. This loads any object needed for any epoch after reference
        #Will select appropriate subset of this in the loop below.
        start_initialize = time.clock()
        print('Reference epoch', epoch_ref)
        ra_dup, dec_dup, times_dup, quads_dup, events_dup = initialize_duplicates_set(epoch_ref,dt,epochs,epoch_timestamps)
        print('Time to initialize duplicate search: ', time.clock() - start_initialize)

        #Loop over each epoch:
        for i in range(0,len(epochs)):
            print('Field = ',fld,' Epoch = ',epochs[i].split('/')[-1])
            start_epoch = time.clock()

            #Compare epoch baseline for this field.
            if not epoch_timestamps[i] >= epoch_ref:
                continue

            # Previous method: Preload duplicate comparisons for this epoch only:
            # start_initialize = time.clock()
            # ra_comp, dec_comp = initialize_duplicates(epoch_timestamps[i],dt,epochs,epoch_timestamps)
            # print('Time to initialize duplicate search: ',time.clock()-start_initialize)

            # New method: identify which members of the initialized array are appropriate for this epoch:
            # This is now done as a function of quadrant.
            day_max = epoch_timestamps[i]
            day_min = epoch_timestamps[i] - timedelta(days=dt)
            for quad in quads_all:
                s2 = Quadrant.objects.get(name=quad)

                index = np.where([((times_dup[m] < day_max) and (times_dup[m] > day_min) and (quads_dup[m] == quad)) for m in range(len(times_dup))])[0]
                ra_comp = [ra_dup[m] for m in index]
                dec_comp = [dec_dup[m] for m in index]

                # Move on if nothing to compare against:
                if not len(ra_comp) > 0:
                    continue

                # Previously: went into epoch folder and grabbed ra/dec again.
                # New method: use info in the duplicate initialized list:
                index2 = np.where([((times_dup[m] == epoch_timestamps[i]) and (quads_dup[m] == quad)) for m in range(len(times_dup))])[0]
                events_epoch = [events_dup[m] for m in index2]
                ra_epoch = [ra_dup[m] for m in index2]
                dec_epoch = [dec_dup[m] for m in index2]
                #events = glob.glob(epochs[i]+'/'+quad+'/*.pdf')
                print(quad,' Number of events to check ',len(events_epoch), 'against ', len(ra_comp))

                # Check event versus database and for duplicates
                for k in range(0,len(events_epoch)):


                    cand0 = Candidate(ra=ra_epoch[k], dec=dec_epoch[k], date_disc=epoch_timestamps[i], full_photom=False)

                    # check if already in db, if it is, then Flag1 = True:
                    # Only check against proper field and quadrant
                    Flag1 = False
                    for tt in Candidate.objects.filter(field=s1).filter(quadrant=s2):
                        if Candidate.is_same_target(tt, cand0):
                            Flag1 = True
                            break

                    # If it is in database, move on to next event.:
                    if Flag1:
                        continue

                    # Check for previous detections based on pre-initialized set of ra/dec.
                    counter = 1 #Keep track of number of detections.

                    for j in range(0,len(ra_comp)):
                        if counter >= nd:
                            break #This just saves time, if we already know we will add no need to continue checking.
                        elif great_circle_distance(ra_epoch[k],dec_epoch[k],ra_comp[j],dec_comp[j]) < (2.0/3600.0):
                            counter = counter + 1

                    # If counter > required # detections, then add to database:
                    if counter >= nd:
                        # Grab other info for database
                        event_f = events_epoch[k]
                        #event_txt = event_f.split('/')[-1].split('.')
                        #field_dir = event_txt[0]
                        #quad_dir = event_txt[1]

                        #s1 = Field.objects.get(subfield=field_dir)
                        #s2 = Quadrant.objects.get(name=quad_dir)
                        s3 = Classification.objects.get(name="candidate")

                        year = epoch_timestamps[i].year
                        n1 = Candidate.objects.filter(field=s1).filter(date_disc__year=year).count() + 1
                        alpha = num2alpha(n1)
                        obj_name = "KSP-" + fld + "_" + str(epoch_timestamps[i].year) + alpha

                        pdf = event_f.split('/')[-1]

                        # Feb 2018: We now tell it to strip the pdf and put the fields in the static area:
                        # Automatically set path to be in the static area.
                        # Event_f is path to pdf:

                        initial_setup = 'source activate testenv && python pdf2jpg.py -p '
                        total_command = initial_setup + event_f
                        subprocess.call(total_command, shell=True)

                        path1 = [jpeg_path(pdf, static_rel=True) + '.B-Filter-SOURCE.jpeg']
                        path2 = [jpeg_path(pdf, static_rel=True) + '.REF.jpeg']
                        path3 = [jpeg_path(pdf, static_rel=True) + '.SOURCE-REF-MMM-mag.jpeg']

                        #OLD: Define paths Base this on discovery date:
                        #if epoch_timestamps[i] < datetime.datetime(2016,12,20,00,00,tzinfo=timezone.utc):
                        #    path1 = glob.glob(base_foxtrot() + jpeg_path(pdf,second=True) + ".B-Filter-SOURCE.jpeg")
                        #    path2 = glob.glob(base_foxtrot() + jpeg_path(pdf,second=True) + ".REF.jpeg")
                        #    path3 = glob.glob(base_foxtrot() + jpeg_path(pdf,second=True) + ".SOURCE-REF-*-mag.jpeg")
                        #else:
                        #    path1 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".B-Filter-SOURCE.jpeg")
                        #    path2 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".REF.jpeg")
                        #    path3 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".SOURCE-REF-*-mag.jpeg")

                        if not len(path1) > 0:
                            path1 = ['kmtshi/images/nojpeg.jpg']
                        if not len(path2) > 0:
                            path2 = ['kmtshi/images/nojpeg.jpg']
                        if not len(path3) > 0:
                            path3 = ['kmtshi/images/nojpeg.jpg']

                        # Actually modify the candidate:
                        cand0.name = obj_name
                        cand0.field = s1
                        cand0.quadrant = s2
                        cand0.classification = s3
                        cand0.disc_im = path1[0]
                        cand0.disc_ref = path2[0]
                        cand0.disc_sub = path3[0]

                        print('New Candidate= ',cand0.name,' File= ',pdf)
                        cand0.save()
                        new_cands.append(cand0.pk)

                        # Call script to gather jpeg image for this event
                        # jpeg = cjpeg(cand0.pk)
                        # print(jpeg)
                        #Call script to gather photom for this event
                        #photom = cphotom(cand0.pk)
                        #print(photom)

            print('Total time for epoch (no photom): ',time.clock()-start_epoch)

            #Update the last epoch checked for this field once done searching that epoch.
            fld_db.last_date = epoch_timestamps[i]
            fld_db.save()

        #################################################################################
        #Update photometry and jpeg for all new_cands that were identified in this field.
        time_photom = time.clock()

        #Move onto next field if there were no new targets.
        if not len(new_cands) > 0:
            continue

        #We need to create lists of pk's separated by quadrants
        quads = [Candidate.objects.get(pk=v).quadrant.name for v in new_cands]
        for quad in set(quads):
            index = np.where([quad_i == quad for quad_i in quads])[0]
            pk_quad = [new_cands[x] for x in index]

            #update the photom and jpegs for this quadrant
            jpeg = cjpeg_list(pk_quad)
            print(jpeg)
            photom = cphotom_list(pk_quad,initial_pass=True)
            print(photom)

        print('Total time to update jpeg and initial photom for ',len(new_cands),' objects = ',time.clock()-time_photom)

if __name__ == "__main__":
    main(sys.argv[1:])