'''This program goes through the entire database and identified jpeg images that are currently linked to.
It then copies those files into a similar file structure within the /static stucture of the kmtshi app.
This will make it possible to host/serve those files from another computer.'''

import os
import sys
import getopt
import glob
import datetime
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

from kmtshi.models import Candidate,jpegImages
from kmtshi.base_directories import base_gdrive,jpeg_path

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
            fld_paths = glob.glob(base_gdrive()+'/*-*')
            flds = [f.split('/')[-1] for f in fld_paths]
        else:
            # Sort fields into strings:
            flds_st = str(flds[1:len(flds)-1])
            flds = flds_st.split(',')
        print('fields ',flds,' will be processed')

