'''Basic file which will be called to search a kmtnet field for new transients'''

#Django set-up:
import os,sys,getopt
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

#kmtshi set-up:
from kmtshi.models import Field,Quadrant,Classification,Candidate
from kmtshi.base_directories import base_data,base_foxtrot,base_gdrive,jpeg_path
from kmtshi.dates import dates_from_filename
from kmtshi.coordinates import coords_from_filename

#Other set-up
import glob
from datetime import timedelta

###################################################################################
def main(argv):
    flds = [] #fields to search
    nd = 2  #number of detections
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
        #Sort fields into strings:
        flds_st = str(flds[1:len(flds)-1])
        flds = flds_st.split(',')
        print('fields ',flds,' will be searched')
        print(nd,' detections within ',dt,' days will be required')

    #We are now armed with the proper fields etc.  Continue to do actual search:
    #Step 1: For a given subfield, identify the gdrive folders:
    for fld in flds:
        #get database field for use:
        fld_db = Field.objects.get(subfield=fld)
        epoch_ref = fld_db.last_date

        #Grab files for epochs.
        epochs = glob.glob(base_foxtrot()+base_gdrive()+fld+'/*')

        #In order to facilitate checking for multiple detections,within a timeframe:
        #I need to select epochs that are within that timeframe before given epoch.
        epoch_timestamps = [dates_from_filename('20'+epoch_f.split('/')[-1].split('.')[0]) for epoch_f in epochs]

        #Loop over each epoch:
        for i in range(0,len(epochs)):
            print('Field = ',fld,' Epcoh = ',epochs[i].split('/')[-1])

            #Compare epoch baseline for this field.
            if not epoch_timestamps[i] > epoch_ref:
                continue

            #If it is after the reference epoch, then go into the folder and get list of sources:
            #NB: Need to reset once I'm not on FOXTROT ANYMORE. Only have Q2 for data, but gdrive for all.
            events = glob.glob(epochs[i]+'/Q2/*.pdf')

            #check if event is already in db:
            for event_f in events:
                event_txt = event_f.split('/')[-1].split('.')

                #grab ra to check if event is in database already:
                c = coords_from_filename(event_txt[5])
                c_ra = c.ra.deg #"{:12.6f}".format(c.ra.deg)
                c_dec = c.dec.deg #"{:12.6f}".format(c.dec.deg)

                cand0 = Candidate(ra=c_ra, dec=c_dec, date_disc=epoch_timestamps[i])

                #check if already in db, if it is, then Flag1 = True:
                Flag1 = False
                for tt in Candidate.objects.all():
                    test = Candidate.is_same_target(tt, cand0)
                    if test:
                        Flag1 = True
                        break

                #If it is in database, move on to next event, otherwise check for another detection:
                if Flag1:
                    continue

                #Check for other detections.
                #Identify which other files I need to search, based on days previous.
                day_min = epoch_timestamps[i] - timedelta(days=dt)
                day_max = epoch_timestamps[i]

                #print('Checking for multiple detections')
                counter = 1 #Keep track of number of detections.

                # Ideally, we would step through the numbers backwards, so the FIRST date it
                # will come accross is the one immediately prior to this one (as opposed to 10 days prior)
                for j in range(len(epoch_timestamps)-1,-1,-1):
                    if counter >= nd:
                        break #This just saves time, if we already know we will add no need to continue checking.

                    if ((epoch_timestamps[j] < day_max) and (epoch_timestamps[j] > day_min)):
                        #Date in range. Check for other detections within 1"
                        #Grab pdf candidates in this epoch.
                        events_ch = glob.glob(epochs[j] + '/*/*.pdf')
                        for event_ch_f in events_ch:
                            event_ch_txt = event_ch_f.split('/')[-1].split('.')
                            c_ch = coords_from_filename(event_ch_txt[5])
                            cand_ch = Candidate(ra=c_ch.ra.deg,dec=c_ch.dec.deg,date_disc=epoch_timestamps[j])

                            #Check if same:
                            if Candidate.is_same_target(cand0,cand_ch):
                                counter = counter + 1
                                break #This sends it on to check the next date
                    else:
                        continue #If date not in range, move on to next date

                #Should have now checked over all the dates in a range.
                # If counter > required # detections, then add to database:
                if counter >= nd:

                    #Gather additional parameters for the database:
                    field_dir = event_txt[0]
                    quad_dir = event_txt[1]
                    s1 = Field.objects.get(subfield=field_dir)
                    s2 = Quadrant.objects.get(name=quad_dir)
                    s3 = Classification.objects.get(name="candidate")

                    n1 = Candidate.objects.filter(field=s1).count() + 1
                    obj_name = "KSP-" + field_dir + "_" + str(epoch_timestamps[i].year) + '-' + str(n1)

                    pdf = event_f.split('/')[-1]

                    #These will now throw an error if they do not exist.
                    path1 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".B-Filter-SOURCE.jpeg")[0]
                    path2 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".REF.jpeg")[0]
                    path3 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".SOURCE-REF-*-mag.jpeg")[0]

                    #Actually modify the candidate:
                    cand0.name = obj_name
                    cand0.field = s1
                    cand0.quadrant = s2
                    cand0.classification = s3
                    cand0.disc_im = path1
                    cand0.disc_ref = path2
                    cand0.disc_sub = path3

                    print('New Candidate= ',cand0.name,' File= ',pdf)
                    #cand0.save()

                    #Call script to gather photom for this event
                    photom = kmtshi_cphotom.py(cand0.pk)
                    print(photom)
                    #Call script to gather jpeg image for this event
                    jpeg = kmtshi_cjpeg.py(cand0.pk)

        #Update the 'last epoch checked for this field:
        fld_db.last_date = max(epoch_timestamps)
        #fld_db.save()


if __name__ == "__main__":
    main(sys.argv[1:])