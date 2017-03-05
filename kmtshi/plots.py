'''This defines a series of bokeh plots that I can call from views.'''

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components

from kmtshi.models import Field,Quadrant,Classification,Candidate,Comment,PngImages,Photometry

import numpy as np

################################################################################################

def MagAuto_FiltersPlot(candidate_id):
    '''This produces a bokeh plot that contains all of the
    BVI MAG_AUTO points from the photometry database for candidate with
    pk given by candidate id.'''

    c1 = Candidate.objects.get(pk=candidate_id)
    filters = ['B', 'V', 'I']
    colors = ['Blue', 'Cyan', 'SeaGreen', 'SpringGreen', 'Red', 'Salmon']

    # Set up the plot:
    p = figure(title="Raw Image SExtractor Photometry", x_axis_label='MJD (days)', y_axis_label='mag',
               y_range=[22.5, 13],tools='pan,box_zoom,wheel_zoom,box_select,crosshair,reset,save,resize')

    # Loop over the filters, add to the plot:
    for i in range(0, len(filters)):
        p1 = Photometry.objects.filter(candidate=c1).filter(filter=filters[i])
        p1_r = p1.filter(flag=True)
        p1_l = p1.filter(flag=False)

        mag_auto_r = np.array([p.mag_auto for p in p1_r])
        dmag_auto_r = np.array([p.dmag_auto for p in p1_r])
        mjd_auto_r = np.array([p.obs_mjd for p in p1_r])

        mag_ap_l = np.array([p.mag_ap for p in p1_l])
        mjd_ap_l = np.array([p.obs_mjd for p in p1_l])

        # Add this filter to the plot:
        p.circle(mjd_auto_r, mag_auto_r, legend=filters[i] + " mag_auto Real", line_width=2, size=8,
                 fill_color=colors[2 * i + 1], line_color=colors[2 * i])
        p.circle(mjd_ap_l, mag_ap_l, legend=filters[i] + " mag Limits", line_width=2, size=8,
                 fill_color="white", line_color=colors[2 * i])

    script, div = components(p, CDN)

    return script, div

