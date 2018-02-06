'''This is the routine that actually takes an individual object and will physically move
all the jpegs that are referenced by that object to the /static area'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

from kmtshi.models import Candidate,jpegImages
from kmtshi.base_directories import base_static_image
from PIL import Image
from shutil import copyfile

def jpeg2static(candidate,errorfile):
    '''
    :param candidate: A django database object to run on.
    :param errorfile: A file that errors can be written to (should already be open when passed here)
    '''


    jpeg_list = jpegImages.objects.filter(candidate=candidate)

    jpeg_m_list = jpeg_list.filter(B_image__icontains='/home/mdrout')

    # Loop over the list of jpegs:
    for jpeg in jpeg_list:

        # Grab path to all six image:
        file_B_i = jpeg.B_image.name
        file_Bref_i = jpeg.Bref_image.name
        file_Bsub_i = jpeg.Bsub_image.name
        file_B_prev_i = jpeg.B_prev_im.name
        file_V_prev_i = jpeg.V_prev_im.name
        file_I_prev_i = jpeg.I_prev_im.name

        # identify directory depends on whether it is in the my home directory of the ksp area:
        if jpeg in jpeg_m_list:
            folder_base = ''.join([a+'/' for a in file_B_i.split('/')[3:-1]])
        else:
            folder_base = ''.join([a + '/' for a in file_B_i.split('/')[2:-1]])

        folder = base_static_image()+folder_base

        # Make sure that the folder exists in the /static area:
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Create strings for path to new images:
        file_B_n = folder+file_B_i.split('/')[-1]
        file_Bref_n = folder+file_Bref_i.split('/')[-1]
        file_Bsub_n = folder+file_Bsub_i.split('/')[-1]
        file_B_prev_n = folder+file_B_prev_i.split('/')[-1]
        file_V_prev_n = folder+file_V_prev_i.split('/')[-1]
        file_I_prev_n = folder+file_I_prev_i.split('/')[-1]

        files_i = [file_B_i,file_Bref_i,file_Bsub_i,file_B_prev_i,file_V_prev_i,file_I_prev_i]
        files_n = [file_B_n,file_Bref_n,file_Bsub_n,file_B_prev_n,file_V_prev_n,file_I_prev_n]

        # Copy the files. If if came from my home directory, use Pillow to flip y direction.
        Missing  = False
        if jpeg in jpeg_m_list:
            for x in range(len(files_i)):
                if os.path.exists(files_i[x]):
                    obj = Image.open(files_i[x])
                    rot = obj.transpose(Image.FLIP_TOP_BOTTOM)
                    rot.save(files_n[x])
                else:
                    Missing = True

        else:
            for x in range(len(files_i)):
                if os.path.exists(files_i[x]):
                    copyfile(files_i[x], files_n[x])
                else:
                    Missing = True


        if Missing:
            outline = folder_base + ' \n'
            errorfile.write(outline)

    # Check if the disim have already been copied, if not copy them over.
    discim = candidate.disc_im.name
    discsub = candidate.disc_sub.name
    discref = candidate.disc_ref.name

    if '/home/mdrout' in discim:
        folder_base2 = ''.join([a + '/' for a in discim.split('/')[3:-1]])
    else:
        folder_base2 = ''.join([a + '/' for a in discim.split('/')[2:-1]])

    folder = base_static_image() + folder_base2

    if not os.path.exists(folder):
        os.makedirs(folder)

        Missing = False
        #Define new outputs
        discim_n = folder+discim.split('/')[-1]
        discsub_n = folder+discsub.split('/')[-1]
        discref_n = folder+discref.split('/')[-1]

        dis_i = [discim,discsub,discref]
        dis_n = [discim_n,discsub_n,discref_n]

        # Copy over given each case:
        if '/home/mdrout' in discim:
            for x in range(len(dis_i)):
                if os.path.exists(dis_i[x]):
                    obj = Image.open(dis_i[x])
                    rot = obj.transpose(Image.FLIP_TOP_BOTTOM)
                    rot.save(dis_n[x])
                else:
                    Missing = True

        else:
            for x in range(len(dis_i)):
                if os.path.exists(dis_i[x]):
                    copyfile(dis_i[x], dis_n[x])
                else:
                    Missing = True

        if Missing:
            outline = folder_base2 + ' \n'
            errorfile.write(outline)

    errorfile.close()

    message = 'complete'
    return message