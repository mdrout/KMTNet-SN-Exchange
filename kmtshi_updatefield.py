'''This code will update the fields that are in the database'''

#Django set-up:
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

#Other set-up:
from kmtshi.models import Field,Quadrant,Classification
from kmtshi.base_directories import base_data,base_foxtrot
import glob


#Search through directories and initialize the fields
#default should be set so that when first created ref_time = 2014.
field_path = glob.glob(base_foxtrot()+base_data()+'*/*')

for f in field_path:

    sub_fld = f.split('/')[-1]
    fld = f.split('/')[-2]

    ft = Field.objects.filter(name=fld,subfield=sub_fld)
    if len(ft) < 1:
        ff = Field.objects.create(name=fld,subfield=sub_fld)
        print('Added ',fld,sub_fld)