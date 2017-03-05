import datetime
import pytz

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
    timestamp = datetime.datetime(y, m, d, h, s)
    timestamp = timestamp.replace(tzinfo=pytz.utc)
    return timestamp
