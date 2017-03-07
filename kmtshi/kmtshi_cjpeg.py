'''This is a routine that can be called in order to either initialize
or update the database of jpeg postage stamp images for a given candidate'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")

#continue on to rest:
import django
django.setup()

from kmtshi.models import Candidate,jpegImages

from kmtshi.dates import dates_from_filename
from kmtshi.coordinates import great_circle_distance,coords_from_filename
import datetime,pytz,glob