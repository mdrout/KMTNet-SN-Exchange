'''This is the routine that actually takes an individual object and will physically move
all the jpegs that are referenced by that object to the /static area

There is aso another routine which take an object as an input an actually changed its database
entry to now point to the /static area for its jpeg images.'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")
import django
django.setup()

from kmtshi.models import Candidate,jpegImages
from kmtshi.base_directories import base_static_image,base_static_rel
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

    message = 'complete'
    return message



def path2static(candidate):
    '''This routine is a one off to change the ImageFields in the database that used to point to other
    areas on sn1987a to now point to the actual /static area within kmtshi.
    This updates both the discim ImageFields in the Candidate model itself, as well as all the imagefields in
    the jpegImages associated with this candidate.

    For reference this is what I input for the error smiley face: path1 = ['kmtshi/images/nojpeg.jpg']

    :para candidate: a django candidate which this will be run on.'''

    # Start with the discim; Grab current name:
    discim = candidate.disc_im.name
    discsub = candidate.disc_sub.name
    discref = candidate.disc_ref.name

    # Only run on objects whose path to those files has not been adjusted yet:
    if not 'kmtshi' in discim:

        #As above strip relevant path information from that.
        if '/home/mdrout' in discim:
            folder_base2 = ''.join([a + '/' for a in discim.split('/')[3:-1]])
        else:
            folder_base2 = ''.join([a + '/' for a in discim.split('/')[2:-1]])

        #folder_full = base_static_image() + folder_base2
        folder_rel = base_static_rel() + folder_base2

        # Construct the new name/path as above:
        #discim_n_full = folder_full + discim.split('/')[-1]
        #discsub_n_full = folder_full + discsub.split('/')[-1]
        #discref_n_full = folder_full + discref.split('/')[-1]

        # Check if each of those exists, and assign proper path as a result.
        #if os.path.exists(discim_n_full):
        #    path1 = [folder_rel + discim.split('/')[-1]]
        #else:
        #    path1 = ['kmtshi/images/nojpeg.jpg']

        # Actually, change no matter if the new one exists. Will maintain info on what the anem of the file WAS before deleted.
        path1 = [folder_rel + discim.split('/')[-1]]
        path2 = [folder_rel + discsub.split('/')[-1]]
        path3 = [folder_rel + discref.split('/')[-1]]

        # Save these results in the Candidate Model Instance itself:
        candidate.disc_im = path1[0]
        candidate.disc_ref = path3[0]
        candidate.disc_sub = path2[0]
        candidate.save()

    #Now go through and do the same for the full set of jpegs associates with this object:
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

        if not 'kmtshi' in file_B_i:

        # identify directory depends on whether it is in the my home directory of the ksp area:
            if jpeg in jpeg_m_list:
                folder_base = ''.join([a+'/' for a in file_B_i.split('/')[3:-1]])
            else:
                folder_base = ''.join([a + '/' for a in file_B_i.split('/')[2:-1]])

            #folder_full = base_static_image() + folder_base
            folder_rel = base_static_rel() + folder_base

            # Construct the full new name/path as above:
            #file_B_n = folder_full + file_B_i.split('/')[-1]
            #file_Bref_n = folder_full + file_Bref_i.split('/')[-1]
            #file_Bsub_n = folder_full + file_Bsub_i.split('/')[-1]
            #file_B_prev_n = folder_full + file_B_prev_i.split('/')[-1]
            #file_V_prev_n = folder_full + file_V_prev_i.split('/')[-1]
            #file_I_prev_n = folder_full + file_I_prev_i.split('/')[-1]

            # Check if each of those exists, and assign proper path as a result.
            path1 = [folder_rel + file_B_i.split('/')[-1]]
            path2 = [folder_rel + file_Bref_i.split('/')[-1]]
            path3 = [folder_rel + file_Bsub_i.split('/')[-1]]
            path4 = [folder_rel + file_B_prev_i.split('/')[-1]]
            path5 = [folder_rel + file_V_prev_i.split('/')[-1]]
            path6 = [folder_rel + file_I_prev_i.split('/')[-1]]

            jpeg.B_image = path1[0]
            jpeg.Bref_image = path2[0]
            jpeg.Bsub_image = path3[0]
            jpeg.B_prev_im = path4[0]
            jpeg.V_prev_im = path5[0]
            jpeg.I_prev_im = path6[0]

            jpeg.save()

    message = 'complete'
    return message