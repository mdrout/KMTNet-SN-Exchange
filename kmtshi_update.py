"""This will eventually be the program which can be called to update the photomety
on a list of events already in the database. At the momembet I am using it to
trouble shoot the photom and jpeg addition programs."""

#Django set-up:
import os,sys,getopt
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

#kmtshi set-up:
from kmtshi.models import Field,Quadrant,Classification,Candidate
from kmtshi.base_directories import base_foxtrot,base_gdrive,jpeg_path
from kmtshi.dates import dates_from_filename
from kmtshi.coordinates import coords_from_filename,great_circle_distance,initialize_duplicates_set
from kmtshi.kmtshi_jpeg import cjpeg_list
from kmtshi.kmtshi_photom import cphotom_list
from kmtshi.alphabet import num2alpha

#Other set-up
import glob,time
import numpy as np
from datetime import timedelta


################################################################################
#List of candidates, pks.
c1 = Candidate.objects.all()
new_cands = [c.pk for c in c1]

#################################################################################
# #Update photometry and jpeg for all new_cands that were identified in this field.
time_photom = time.clock()

#Move onto next field if there were no new targets.
if not len(new_cands) > 0:
    print('No candidates listed for update')
    sys.exit()

#We need to create lists of pk's separated by quadrants
quads = [Candidate.objects.get(pk=v).quadrant.name for v in new_cands]
for quad in set(quads):

    index = np.where([quad_i == quad for quad_i in quads])[0]
    pk_quad = [new_cands[x] for x in index]

    #update the photom and jpegs for this quadrant
    jpeg = cjpeg_list(pk_quad,check_all=True)
    print(jpeg)
    #photom = cphotom_list(pk_quad)
    #print(photom)

print('Total time to update photom for ',len(new_cands),' objects = ',time.clock()-time_photom)