'''This program goes through the entire database and identified jpeg images that are currently linked to.
It then copies those files into a similar file structure within the /static stucture of the kmtshi app.
This will make it possible to host/serve those files from another computer.

Note: if you initiate the path2static instead, it will update the paths in the ImageFields for the
database items so that they actually point towards the static area.'''

import os
import sys
import getopt
import glob
import datetime
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

from kmtshi.models import Candidate,Field,jpegImages
from kmtshi.base_directories import base_gdrive,jpeg_path
from jpeg2static import jpeg2static, path2static

#Copy bit to submit fields from search:
###################################################################################

def main(argv):
    flds = [] #fields to search
    try:
        opts, args = getopt.getopt(argv,"f:",["fields="])
    except getopt.GetoptError:
        print('jpeg2static.py -f <[list of subfields]>')
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
            fld_paths = glob.glob(base_gdrive() + '/*-1') + glob.glob(base_gdrive() + '/*-2') + glob.glob(base_gdrive() + '/*-9')
            flds = [f.split('/')[-1] for f in fld_paths]
        else:
            # Sort fields into strings:
            flds_st = str(flds[1:len(flds)-1])
            flds = flds_st.split(',')
        print('fields ',flds,' will be processed')

    # Open the error file:
    #errorfile = open('missingfiles.dat','a')

    for fld in flds:
        print('Processing '+fld)
        tstart = time.clock()

        field = Field.objects.get(subfield = fld)
        candidates = Candidate.objects.filter(field = field)

        for cand in candidates:
            #temp = jpeg2static(cand,errorfile)
            temp = path2static(cand)

        print('Time for '+fld, time.clock()-tstart)

    #errorfile.close()

if __name__ == "__main__":
    main(sys.argv[1:])