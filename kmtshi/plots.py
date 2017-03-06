'''This defines a series of bokeh plots that I can call from views.'''

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.layouts import gridplot

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
    p = figure(title="Raw Image SExtractor BVI Photometry", x_axis_label='MJD (days)', y_axis_label='mag',
               y_range=[22.5, 11],tools='pan,box_zoom,wheel_zoom,box_select,crosshair,reset,save,resize',
               width=700,height=450)

    p.background_fill_color = "beige"
    p.background_fill_alpha = 0.5
    p.border_fill_color = "whitesmoke"
    p.min_border = 25

    # Loop over the filters, add to the plot:
    for i in range(0, len(filters)):
        p1 = Photometry.objects.filter(candidate=c1).filter(filter=filters[i])
        p1_r = p1.filter(flag=True)
        p1_l = p1.filter(flag=False)

        mag_auto_r = np.array([p.mag_auto for p in p1_r])
        mjd_auto_r = np.array([p.obs_mjd for p in p1_r])

        mag_ap_l = np.array([p.mag_ap for p in p1_l])
        mjd_ap_l = np.array([p.obs_mjd for p in p1_l])

        # Add this filter to the plot:
        p.circle(mjd_auto_r, mag_auto_r, legend=filters[i] + " mag_auto Real", line_width=2, size=8,
                 fill_color=colors[2 * i + 1], line_color=colors[2 * i])
        p.circle(mjd_ap_l, mag_ap_l, legend=filters[i] + " mag Limits", line_width=2, size=8,
                 fill_color="white", line_color=colors[2 * i])

    pp=gridplot([[p]],toolbar_location="right")
    script, div = components(pp, CDN)

    return script, div

def Mag_FiltersLinkPlot(candidate_id):
    c1 = Candidate.objects.get(pk=candidate_id)
    filters = ['B', 'V', 'I','Bsub']
    colors = ['Blue', 'Cyan', 'SeaGreen', 'SpringGreen', 'Red', 'Salmon','Teal','Cyan']

    #Set up all four plots:
    TOOLS = 'pan,box_zoom,wheel_zoom,box_select,crosshair,reset,save'
    s1 = figure(title="Raw Image B Photom", x_axis_label='MJD (days)', y_axis_label='mag',
                y_range=[22.5, 11], tools=TOOLS,width=350, plot_height=350)
    s2 = figure(title="Raw Image V Photom", x_axis_label='MJD (days)', y_axis_label='mag',
                y_range=[22.5, 11], x_range=s1.x_range, tools=TOOLS,width=350, plot_height=350)
    s3 = figure(title="Raw Image I Photom", x_axis_label='MJD (days)', y_axis_label='mag',
                y_range=[22.5, 11], x_range=s1.x_range, tools=TOOLS,width=350, plot_height=350)
    s4 = figure(title="Bsub Photom", x_axis_label='MJD (days)', y_axis_label='mag',
                y_range=[22.5, 11], x_range=s1.x_range, tools=TOOLS,width=350, plot_height=350)

    s1.background_fill_color = "beige"
    s1.background_fill_alpha = 0.5
    s2.background_fill_color = "beige"
    s2.background_fill_alpha = 0.5
    s3.background_fill_color = "beige"
    s3.background_fill_alpha = 0.5
    s4.background_fill_color = "beige"
    s4.background_fill_alpha = 0.5

    s1.border_fill_color = "whitesmoke"
    s2.border_fill_color = "whitesmoke"
    s2.min_border_right = 25
    s3.border_fill_color = "whitesmoke"
    s4.border_fill_color = "whitesmoke"
    s4.min_border_right = 25

    # Loop over the filters, to gather photom and add to appropriate plot:
    for i in range(0, len(filters)):
        p1 = Photometry.objects.filter(candidate=c1).filter(filter=filters[i])
        p1_r = p1.filter(flag=True)
        p1_l = p1.filter(flag=False)

        mag_auto_r = np.array([p.mag_auto for p in p1_r])
        mjd_auto_r = np.array([p.obs_mjd for p in p1_r])

        mag_ap_l = np.array([p.mag_ap for p in p1_l])
        mjd_ap_l = np.array([p.obs_mjd for p in p1_l])

        # Create plot depending on filter:
        if filters[i] == 'B':
            s1.circle(mjd_auto_r, mag_auto_r, legend="Real", line_width=2, size=8,
                 fill_color=colors[2 * i + 1], line_color=colors[2 * i])
            s1.circle(mjd_ap_l, mag_ap_l, legend="Limits", line_width=2, size=8,
                 fill_color="white", line_color=colors[2 * i])
        if filters[i] == 'V':
            s2.circle(mjd_auto_r, mag_auto_r, legend="Real", line_width=2, size=8,
                 fill_color=colors[2 * i + 1], line_color=colors[2 * i])
            s2.circle(mjd_ap_l, mag_ap_l, legend="Limits", line_width=2, size=8,
                 fill_color="white", line_color=colors[2 * i])
        if filters[i] == 'I':
            s3.circle(mjd_auto_r, mag_auto_r, legend="Real", line_width=2, size=8,
                 fill_color=colors[2 * i + 1], line_color=colors[2 * i])
            s3.circle(mjd_ap_l, mag_ap_l, legend="Limits", line_width=2, size=8,
                 fill_color="white", line_color=colors[2 * i])
        if filters[i] == 'Bsub':
            s4.circle(mjd_auto_r, mag_auto_r, legend="Real", line_width=2, size=8,
                 fill_color=colors[2 * i + 1], line_color=colors[2 * i])
            s4.circle(mjd_ap_l, mag_ap_l, legend="Limits", line_width=2, size=8,
                 fill_color="white", line_color=colors[2 * i])

    #Create grid plot:
    p = gridplot([[s1, s2], [s3, s4]],toolbar_location="right")
    script, div = components(p, CDN)

    return script, div
