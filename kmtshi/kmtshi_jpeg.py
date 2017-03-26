'''This is a routine that can be called in order to either initialize
or update the database of jpeg postage stamp images for a given candidate'''

import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")

#continue on to rest:
import django
django.setup()
from django.utils import timezone

from kmtshi.models import Candidate,jpegImages,Photometry
from kmtshi.dates import dates_from_filename
from kmtshi.coordinates import great_circle_distance,coords_from_filename
from kmtshi.base_directories import base_data,base_foxtrot,jpeg_path
import datetime,glob,time


def cjpeg(candidate_id):
    '''This will find the jpeg images for a specific candidate'''
    c1 = Candidate.objects.get(pk=candidate_id)

    #Define ref time to search based on info in the photometry database already.
    #NB: we are not using the jpeg database itself, because this will lead to
    #redudant searches for true transients that are non-detected afterward.
    #This does mean that I should always run BEFORE photom updates.
    t1 = Photometry.objects.filter(candidate=c1).order_by('-obs_date')
    if len(t1) > 0:
        timestamp_ref = t1[0].obs_date
    else:
        timestamp_ref = datetime.datetime(2014,1,1,00,00,tzinfo=timezone.utc)

    ####################################################################
    # Set-up places to searh:
    base = base_foxtrot() + base_data() + c1.field.name + '/' + c1.field.subfield + '/' + c1.quadrant.name + '/B_Filter/Subtraction/JPEG_TV_IMAGES/'

    #Determine folders to search:
    #They are of the form: "N2188-1.Q0.B.161228_2045.S.061239D772-332826D7.20D204.0D020.0036"
    #Within these folders are jpeg images.

    ffnames = glob.glob(base + '*')
    for ffname in ffnames:
        t2 = ffname.split('/')[-1].split('.')

        # Test the time compared to reference:
        timestamp = dates_from_filename('20' + t2[3])

        #Move on if the time isn't after the reference.
        if not (timestamp > timestamp_ref):
            continue

        #Check ra/dec against candidate ra/dec:
        coords = coords_from_filename(t2[5])
        if great_circle_distance(c1.ra, c1.dec, coords.ra.deg, coords.dec.deg) < (1.0 / 3600.0):

            #Candidate is the within 1". Populate the jpg database with files.
            ims = jpegImages(candidate=c1, date_txt=t2[3], obs_date=timestamp)

            pdf=ffname.split('/')[-1]+'.pdf'

            path1 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".B-Filter-SOURCE.jpeg")
            path2 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".REF.jpeg")
            path3 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".SOURCE-REF-*-mag.jpeg")
            path4 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".B.*.jpeg")
            path5 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".V.*.jpeg")
            path6 = glob.glob(base_foxtrot()+jpeg_path(pdf) + ".I.*.jpeg")

            if not len(path1) > 0:
                path1 = 'kmtshi/images/nojpeg.jpg'
            if not len(path2) > 0:
                path2 = 'kmtshi/images/nojpeg.jpg'
            if not len(path3) > 0:
                path3 = 'kmtshi/images/nojpeg.jpg'
            if not len(path4) > 0:
                path4 = 'kmtshi/images/nojpeg.jpg'
            if not len(path5) > 0:
                path5 = 'kmtshi/images/nojpeg.jpg'
            if not len(path6) > 0:
                path6 = 'kmtshi/images/nojpeg.jpg'

            ims.B_image = path1[0]
            ims.Bref_image = path2[0]
            ims.Bsub_image = path3[0]
            ims.B_prev_im = path4[0]
            ims.V_prev_im = path5[0]
            ims.I_prev_im = path6[0]

            ims.save()

    txt_out='Jpeg images have been updated for object '+str(c1.name)
    return txt_out


def cjpeg_list(candidate_ids,check_all=False,check_photom=False):
    '''This will find the jpeg images for list of candiates.
    All must be within the same subfield and quadrant.
    It will just pre-initialize several things to make it more efficient.

    :param candidate_ids: list of pk values for events to be checked
    :param check_all: if this is true the reference epoch over which
    time to look will be set to 2014,
    :param check_photom: if true reference epoch based on the last bit
    of photometry in the database for that event.
    Otherwise reference date set by last jpeg image avaliable'''

    ########################################################################
    # Check that all of the candidate_ids have same sub-field and quadrant.
    flds = [Candidate.objects.get(pk=x).field.subfield for x in candidate_ids]
    quads = [Candidate.objects.get(pk=x).quadrant.name for x in candidate_ids]
    if len(set(flds)) > 1:
        print('Not all candidates for jpegs are in same fld')
        sys.exit()
    elif len(set(quads)) > 1:
        print('Not all candidates for jpegs are in same quadrant')
        sys.exit()

    #########################################################################
    ##Initalize a list of reference timestamps for all of the input candidates.
    timestamps_ref = []
    for y in range(0, len(candidate_ids)):
        c1 = Candidate.objects.get(pk=candidate_ids[y])

        # Define ref time to search based on info in the photometry database already.
        # Unless check_all has been given.
        # See commentary above.
        # Third option: check_photom now applied to above case of photometry.
        # Otherwise based on the last JPEG which is actually there.
        if check_all:
            timestamps_ref.append(datetime.datetime(2014, 1, 1, 00, 00, tzinfo=timezone.utc))
        else:
            if check_photom:
                t1 = Photometry.objects.filter(candidate=c1).order_by('-obs_date')
            else:
                t1 = jpegImages.objects.filter(candidate=c1).order_by('-obs_date')

            if len(t1) > 0:
                timestamps_ref.append(t1[0].obs_date)
            else:
                timestamps_ref.append(datetime.datetime(2014, 1, 1, 00, 00, tzinfo=timezone.utc))

    ####################################################################
    # Set-up places to search for these events:
    base1 = base_data() + c1.field.name + '/' + c1.field.subfield + '/' + c1.quadrant.name + '/B_Filter/Subtraction/JPEG_TV_IMAGES/'

    # Base for early jpegs:
    base2 = base_data(second=True) + c1.field.name + '/' + c1.field.subfield + '/' + c1.quadrant.name + '/B_Filter/Subtraction/JPEG_TV_IMAGES/'

    bases=[base1,base2]

    #Cycle over both the new and the old:
    for b in range(len(bases)):
        base = bases[b]

        #Determine folders to search:
        #They are of the form: "N2188-1.Q0.B.161228_2045.S.061239D772-332826D7.20D204.0D020.0036"
        #All candidates for all epochs have their own folder:

        ffnames = glob.glob(base + '*')

        #Initialize lists of (a) timestamps (b) ra/dec for all of these jpeg folderss.
        t_init = time.clock()
        time_folders = [ffname.split('/')[-1].split('.')[3] for ffname in ffnames]
        timestamp_folders = [dates_from_filename('20'+ffname.split('/')[-1].split('.')[3]) for ffname in ffnames]
        ra_folders = [coords_from_filename(ffname.split('/')[-1].split('.')[5]).ra.deg for ffname in ffnames]
        dec_folders = [coords_from_filename(ffname.split('/')[-1].split('.')[5]).dec.deg for ffname in ffnames]
        print('time to init jpeg = ', time.clock()-t_init)

        #Cycle over the new candidates:
        for j in range(0,len(candidate_ids)):
            c1=Candidate.objects.get(pk=candidate_ids[j])
            #count = 0

            #cycle over the jpeg folders:
            for i in range(0,len(ffnames)):

                #Check the timestamp:
                if (timestamps_ref[j] > timestamp_folders[i]):
                    continue

                #Check the coordinates:
                if great_circle_distance(c1.ra, c1.dec, ra_folders[i], dec_folders[i]) < (1.0 / 3600.0):

                    # Candidate is the within 1". Populate the jpg database with files.
                    ims = jpegImages(candidate=c1, date_txt=time_folders[i], obs_date=timestamp_folders[i])

                    pdf = ffnames[i].split('/')[-1] + '.pdf'

                    if b==0:
                        path1 = glob.glob(base_foxtrot() + jpeg_path(pdf) + ".B-Filter-SOURCE.jpeg")
                        path2 = glob.glob(base_foxtrot() + jpeg_path(pdf) + ".REF.jpeg")
                        path3 = glob.glob(base_foxtrot() + jpeg_path(pdf) + ".SOURCE-REF-*-mag.jpeg")
                        path4 = glob.glob(base_foxtrot() + jpeg_path(pdf) + ".B.*.jpeg")
                        path5 = glob.glob(base_foxtrot() + jpeg_path(pdf) + ".V.*.jpeg")
                        path6 = glob.glob(base_foxtrot() + jpeg_path(pdf) + ".I.*.jpeg")
                    else:
                        path1 = glob.glob(base_foxtrot() + jpeg_path(pdf,second=True) + ".B-Filter-SOURCE.jpeg")
                        path2 = glob.glob(base_foxtrot() + jpeg_path(pdf,second=True) + ".REF.jpeg")
                        path3 = glob.glob(base_foxtrot() + jpeg_path(pdf,second=True) + ".SOURCE-REF-*-mag.jpeg")
                        path4 = glob.glob(base_foxtrot() + jpeg_path(pdf,second=True) + ".B.*.jpeg")
                        path5 = glob.glob(base_foxtrot() + jpeg_path(pdf,second=True) + ".V.*.jpeg")
                        path6 = glob.glob(base_foxtrot() + jpeg_path(pdf,second=True) + ".I.*.jpeg")

                    if not len(path1) > 0:
                        path1 = ['kmtshi/images/nojpeg.jpg']
                    if not len(path2) > 0:
                        path2 = ['kmtshi/images/nojpeg.jpg']
                    if not len(path3) > 0:
                        path3 = ['kmtshi/images/nojpeg.jpg']
                    if not len(path4) > 0:
                        path4 = ['kmtshi/images/nojpeg.jpg']
                    if not len(path5) > 0:
                        path5 = ['kmtshi/images/nojpeg.jpg']
                    if not len(path6) > 0:
                        path6 = ['kmtshi/images/nojpeg.jpg']

                    ims.B_image = path1[0]
                    ims.Bref_image = path2[0]
                    ims.Bsub_image = path3[0]
                    ims.B_prev_im = path4[0]
                    ims.V_prev_im = path5[0]
                    ims.I_prev_im = path6[0]

                    ims.save()
                    #count = count+1

            #if count > 0:
            #    print(count)

    txt_out='Jpeg images have been updated list of objects'
    return txt_out
