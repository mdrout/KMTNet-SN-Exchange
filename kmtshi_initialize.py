'''This code with initialize the kmtshi database.
It is the first code that should be run on sn1987a
It will populate the most basic fields of the database
(Fields, Quadrants, Classifications, etc) so that other
code can be run to search for and add candidates'''

#Django set-up:
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

#Other set-up:
from kmtshi.models import Field,Quadrant,Classification
from kmtshi.base_directories import base_data,base_foxtrot
import glob

#Set-up the four quadrants
q0 = Quadrant.objects.create(name="Q0")
q1 = Quadrant.objects.create(name="Q1")
q2 = Quadrant.objects.create(name="Q2")
q3 = Quadrant.objects.create(name="Q3")

#Set-up Initial Classification Options
c0 = Classification.objects.create(name="candidate")
c1 = Classification.objects.create(name="bad subtraction")
c2 = Classification.objects.create(name="real transient")
c3 = Classification.objects.create(name="stellar source: general")
c4 = Classification.objects.create(name="stellar source: variable")
c5 = Classification.objects.create(name="unsure")
c6 = Classification.objects.create(name="junk")

#Search through directories and initialize the fields
#default should be set so that when first created ref_time = 2014.
field_path = glob.glob(base_foxtrot()+base_data()+'*/*')

for f in field_path:

    sub_fld = f.split('/')[-1]
    fld = f.split('/')[-2]
    ff = Field.objects.create(name=fld,subfield=sub_fld)
