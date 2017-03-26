"""This code takes a list of pks from the database and will fix the path
to their discovery image jpegs (if something went awry)"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

import glob
from kmtshi.models import Candidate,jpegImages
from kmtshi.coordinates import coords_from_filename, great_circle_distance
from kmtshi.dates import filename_from_dates

# ###############################################################################
# List of candidates, pks.
# c1 = Candidate.objects.all()

#List of events which have missing discovery images:
c1 = Candidate.objects.filter(disc_im='kmtshi/images/nojpeg.jpg')
new_cands = [c.pk for c in c1]

# ################################################################################
count = 0
for nc in new_cands:
    c1 = Candidate.objects.get(pk=nc)

    # Read in discovery date and other important info:
    date = c1.date_disc
    fld = c1.field.name
    sfld = c1.field.subfield
    quad = c1.quadrant.name
    ra = c1.ra
    dec = c1.dec

    # Turn the discovery datetime object back into a string..
    date_txt = filename_from_dates(date)

    # Use this plus the field info to find the right candidate/jpeg images.

    # Load ones from proper day:
    # base = '/data/ksp/data/PROCESSED/' + fld + '/' + sfld + '/' + quad + '/B_Filter/Subtraction/JPEG_TV_IMAGES/'
    base = '/home/mdrout/ksp/data/PROCESSED/' + fld + '/' + sfld + '/' + quad + '/B_Filter/Subtraction/JPEG_TV_IMAGES/'
    events_f = glob.glob(base+'*'+date_txt+'*')
    events = [e.split('/')[-1] for e in events_f]

    # Cycle over events to identify which one has the proper ra/dec
    Flag = False  # Flag for whether we have found jpeg image at the proper location.
    for event in events:
        c_check = coords_from_filename(event.split('.')[5])
        if great_circle_distance(ra, dec, c_check.ra.deg, c_check.dec.deg) < (1.0/3600.0):
            # This is a match, define the paths:
            base_event = base+event+'/'+event

            path1 = glob.glob(base_event + ".B-Filter-SOURCE.jpeg")
            path2 = glob.glob(base_event + ".REF.jpeg")
            path3 = glob.glob(base_event + ".SOURCE-REF-*-mag.jpeg")

            if not len(path1) > 0:
                path1 = ['kmtshi/images/nojpeg.jpg']
            if not len(path2) > 0:
                path2 = ['kmtshi/images/nojpeg.jpg']
            if not len(path3) > 0:
                path3 = ['kmtshi/images/nojpeg.jpg']

            c1.disc_im = path1[0]
            c1.disc_ref = path2[0]
            c1.disc_sub = path3[0]
            c1.save()
            Flag = True
            count = count+1
            break

    # If no match was found: assign nojpeg image:
    if not Flag:
        path1 = ['kmtshi/images/nojpeg.jpg']
        path2 = ['kmtshi/images/nojpeg.jpg']
        path3 = ['kmtshi/images/nojpeg.jpg']

        c1.disc_im = path1[0]
        c1.disc_ref = path2[0]
        c1.disc_sub = path3[0]
        c1.save()

print('Found new files for ',count,' of ',len(new_cands))
