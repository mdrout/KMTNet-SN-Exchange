"""This is just going to get info from the database and write out an ascii file"""

from kmtshi.models import Field,Quadrant,Classification,Candidate,Comment,jpegImages,Photometry
import numpy as np

def output_lc(candidate_id):
    '''For a given candidate id, write out the kmtshi photometry.'''

    c1 = Candidate.objects.get(pk=candidate_id)
    filters = ['B', 'V', 'I','Bsub']

    name = str(c1.name)+'BVIBsub.dat'
    print(name)
    #lab = "Photometry for "+c1.name+"\n"
    #with open(name,'wb') as f:
    #    f.write('test')

    for i in range(0, len(filters)):
        p1 = Photometry.objects.filter(candidate=c1).filter(filter=filters[i])
        p1_r = p1.filter(flag=True)
        p1_l = p1.filter(flag=False)

        mag_auto_r = np.array([p.mag_auto for p in p1])
        mjd_auto_r = np.array([p.obs_mjd for p in p1])
        dmag_auto_r = np.array([p.dmag_auto for p in p1])

        #mag_ap_l = np.array([p.mag_ap for p in p1_l])
        #mjd_ap_l = np.array([p.obs_mjd for p in p1_l])

        for j in range(0,len(p1)):
            string = str(mjd_auto_r[j])+' '+filters[i]+' '+str(mag_auto_r[j])+' '+str(dmag_auto_r[j])+'\n'
            #print(string)

            with open(name,"a") as t:
                t.write(string)


    Test = 'Finished'
    return Test
