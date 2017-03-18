from django.utils import timezone
import datetime

def dates_from_filename(filestring):
    '''Create a datetime object based on the string
    which is found in many of the kmtshi file names

    :param filestring: input string. Format assumed as: 20170120_0117
    :return: datetime object'''

    y = int(filestring[0:4])
    m = int(filestring[4:6])
    d = int(filestring[6:8])
    h = int(filestring[9:11])
    s = int(filestring[11:13])
    timestamp = datetime.datetime(y, m, d, h, s,tzinfo=timezone.utc)
    return timestamp

def filename_from_dates(date):
    '''Create a file structure 170238_2145 form from a datetime objects

    :param: date datetime object
    :return filestring: input string. Format assumed as: 20170120_0117'''

    y = str(date.year)[2:]
    if len(str(date.month)) < 2:
        m = '0'+str(date.month)
    else:
        m = str(date.month)
    if len(str(date.day)) < 2:
        d = '0'+str(date.day)
    else:
        d = str(date.day)
    if len(str(date.hour)) < 2:
        h = '0'+str(date.hour)
    else:
        h = str(date.hour)
    if len(str(date.minute)) < 2:
        mn = '0'+str(date.minute)
    else:
        mn = str(date.minute)

    # Combine:
    date_txt = y+m+d+'_'+h+mn

    return date_txt