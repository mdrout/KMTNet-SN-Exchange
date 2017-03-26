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


#Copy bit to submit fields from search:
###################################################################################
def main(argv):
    flds = [] #fields to search
    try:
        opts, args = getopt.getopt(argv,"f:",["fields="])
    except getopt.GetoptError:
        print('kmtshi_search.py -f <[list of subfields]>')
        print('--fields also permitted')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-f","--fields"):
            flds = arg
    if len(flds) < 1:
        print('At least one field to search must be specified')
        print('kmtshi_search.py -f <[list of subfields]> ')
        sys.exit(2)
    else:
        if flds == 'all':
            fld_paths = glob.glob(base_gdrive()+'/*-*')
            flds = [f.split('/')[-1] for f in fld_paths]
        else:
            # Sort fields into strings:
            flds_st = str(flds[1:len(flds)-1])
            flds = flds_st.split(',')
        print('fields ',flds,' will be updated')


    ################################################################################
    # List of candidates, pks. for each field:
    for fld in flds:
        f1 = Field.objects.get(subfield=fld)
        c1 = Candidate.objects.filter(field=f1)
        new_cands = [c.pk for c in c1]

        # ################################################################################
        # #Update photometry and jpeg for all new_cands that were identified in this field.
        time_photom = time.clock()

        # Move onto next field if there were no new targets.
        if not len(new_cands) > 0:
            print('No candidates listed for update')
            sys.exit()

        #   We need to create lists of pk's separated by quadrants
        quads = [Candidate.objects.get(pk=v).quadrant.name for v in new_cands]
        for quad in set(quads):
            print(fld,quad)
            index = np.where([quad_i == quad for quad_i in quads])[0]
            pk_quad = [new_cands[x] for x in index]

            #update the photom and jpegs for this quadrant
            #jpeg = cjpeg_list(pk_quad,check_all=True)
            #print(jpeg)
            photom = cphotom_list(pk_quad)
            print(photom)

        print('Total time to update photom for ',fld,' objects = ',time.clock()-time_photom)

if __name__ == "__main__":
    main(sys.argv[1:])