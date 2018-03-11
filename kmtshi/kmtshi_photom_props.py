'''This will serve to measure basic parameters about the photometry of a source'''

import os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmtshi.settings")

# continue on to rest:
import django

django.setup()

from kmtshi.models import Candidate, Photometry, Field, Quadrant
import numpy as np


def photom_props(candidate_list):
    '''grab the B-band photometry associated with a list of events. Return lists of the mean mag and stddev.

    :param candidate_list: list of kmtshi database candidates
    '''

    Bmags = []
    Vmags = []
    Imags = []
    Bstddevs = []

    for cand in candidate_list:
        B_photom = Photometry.objects.filter(candidate=cand).filter(filter='B')
        V_photom = Photometry.objects.filter(candidate=cand).filter(filter='V')
        I_photom = Photometry.objects.filter(candidate=cand).filter(filter='I')

        if len(B_photom) > 0:
            list = [x.mag_auto for x in B_photom]
            Bmag1 = np.nanmean(list)
            Bstddev1 = np.nanstd(list)

            # Reject some outliers (NB: this would remove transients, so do need to be careful; look through):
            list_new = [x for x in list if (x > Bmag1 - 2.5 * Bstddev1)]
            list_new = [x for x in list_new if (x < Bmag1 + 2.5 * Bstddev1)]

            Bmag = np.nanmean(list_new)
            Bstddev = np.nanstd(list_new)
        else:
            Bmag = 0.
            Bstddev = 0.

        if len(V_photom) > 0:
            list = [x.mag_auto for x in V_photom]
            Vmag = np.nanmean(list)
        else:
            Vmag = 0.

        if len(I_photom) > 0:
            list = [x.mag_auto for x in I_photom]
            Imag = np.nanmean(list)
        else:
            Imag = 0.


        Bmags.append(Bmag)
        Vmags.append(Vmag)
        Imags.append(Imag)
        Bstddevs.append(Bstddev)

    return Bmags,Vmags,Imags,Bstddevs



def photom_props_db(candidate_list):
    '''Update mean B, V, I, and Bstddev for set of candidates.
    :param candidate_list: list of kmtshi database candidates
    '''


    for cand in candidate_list:
        B_photom = Photometry.objects.filter(candidate=cand).filter(filter='B').exclude(flag=False)
        V_photom = Photometry.objects.filter(candidate=cand).filter(filter='V').exclude(flag=False)
        I_photom = Photometry.objects.filter(candidate=cand).filter(filter='I').exclude(flag=False)

        #print(cand)

        if len(B_photom) > 0:
            list = [x.mag_auto for x in B_photom]
            Bmag = np.nanmean(list)
            Bstddev = np.nanstd(list)

            if Bstddev > 0.:

                # Reject some outliers (NB: this would remove transients, so do need to be careful; look through):
                list_new = [x for x in list if (x > Bmag - 2.5 * Bstddev)]
                list_new = [x for x in list_new if (x < Bmag + 2.5 * Bstddev)]

                Bmag = np.nanmean(list_new)
                Bstddev = np.nanstd(list_new)
        else:
            Bmag = 99.9
            Bstddev = 0.

        if len(V_photom) > 0:
            list = [x.mag_auto for x in V_photom]
            Vmag = np.nanmean(list)
        else:
            Vmag = 99.9

        if len(I_photom) > 0:
            list = [x.mag_auto for x in I_photom]
            Imag = np.nanmean(list)
        else:
            Imag = 99.9

        #print(cand,Bmag,Vmag,Imag,Bstddev)

        cand.Bmag=Bmag
        cand.Vmag=Vmag
        cand.Imag=Imag
        cand.Bstddev=Bstddev
        cand.save()

        #print(cand, Bmag, Vmag, Imag, Bstddev)

    return 'Updated database for set of events'