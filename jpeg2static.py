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

def jpeg2static(candidate):
    jpeg_list = jpegImages.objects.filter(candidate=candidate)

    jpeg_m_list = jpeg_list.filter(B_image__icontains='/home/mdrout')

    # Handle ones in my home directory:
    for jpeg in jpeg_list:

        # Grab path to all six image:
        file_B_i = jpeg.B_image.name
        file_Bref_i = jpeg.Bref_image.name
        file_Bsub_i = jpeg.Bsub_image.name
        file_B_prev_i = jpeg.B_prev_im.name
        file_V_prev_i = jpeg.V_prev_im.name
        file_I_prev_i = jpeg.I_prev_im.name

        # identify directory depends on whether it is in the 'm' list:
        if jpeg in jpeg_m_list:
            folder_base = ''.join([a+'/' for a in file_B_i.split('/')[3:-1]])
        else:
            folder_base = ''.join([a + '/' for a in file_B_i.split('/')[2:-1]])

        folder = base_static_image()+folder_base

        # Make sure that it exists in the /static area:
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Create strings for path to new images:
        file_B_n = folder+file_B_i.split('/')[-1]
        file_Bref_n = folder+file_Bref_i.split('/')[-1]
        file_Bsub_n = folder+file_Bsub_i.split('/')[-1]
        file_B_prev_n = folder+file_B_prev_i.split('/')[-1]
        file_V_prev_n = folder+file_V_prev_i.split('/')[-1]
        file_I_prev_n = folder+file_I_prev_i.split('/')[-1]

        # Copy the files. If if came from my home directory, use Pillow to flip y direction.
        if jpeg in jpeg_m_list:
            Bim_obj = Image.open(file_B_i)
            Bim_rot = Bim_obj.transpose(Image.FLIP_TOP_BOTTOM)
            Bim_rot.save(file_B_n)

            Bref_obj = Image.open(file_Bref_i)
            Bref_rot = Bref_obj.transpose(Image.FLIP_TOP_BOTTOM)
            Bref_rot.save(file_Bref_n)

            Bsub_obj = Image.open(file_Bsub_i)
            Bsub_rot = Bsub_obj.transpose(Image.FLIP_TOP_BOTTOM)
            Bsub_rot.save(file_Bsub_n)

            Bprev_obj = Image.open(file_B_prev_i)
            Bprev_rot = Bprev_obj.transpose(Image.FLIP_TOP_BOTTOM)
            Bprev_rot.save(file_B_prev_n)

            Vprev_obj = Image.open(file_V_prev_i)
            Vprev_rot = Vprev_obj.transpose(Image.FLIP_TOP_BOTTOM)
            Vprev_rot.save(file_V_prev_n)

            Iprev_obj = Image.open(file_I_prev_i)
            Iprev_rot = Iprev_obj.transpose(Image.FLIP_TOP_BOTTOM)
            Iprev_rot.save(file_I_prev_n)

        else:
            copyfile(file_B_i,file_B_n)
            copyfile(file_Bref_i, file_Bref_n)
            copyfile(file_Bsub_i, file_Bsub_n)
            copyfile(file_B_prev_i, file_B_prev_n)
            copyfile(file_V_prev_i, file_V_prev_n)
            copyfile(file_I_prev_i, file_I_prev_n)

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

        #Define new outputs
        discim_n = folder+discim.split('/')[-1]
        discsub_n = folder+discsub.split('/')[-1]
        discref_n = folder+discref.split('/')[-1]

        # Copy over given each case:
        if '/home/mdrout' in discim:
            discim_obj = Image.open(discim)
            discim_rot = discim_obj.transpose(Image.FLIP_TOP_BOTTOM)
            discim_rot.save(discim_n)

            discsub_obj = Image.open(discsub)
            discsub_rot = discsub_obj.transpose(Image.FLIP_TOP_BOTTOM)
            discsub_rot.save(discsub_n)

            discref_obj = Image.open(discref)
            discref_rot = discref_obj.transpose(Image.FLIP_TOP_BOTTOM)
            discref_rot.save(discref_n)

        else:
            copyfile(discim, discim_n)
            copyfile(discref, discref_n)
            copyfile(discsub, discsub_n)


    message = 'complete'
    return message