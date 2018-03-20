from django.http import HttpResponse,Http404
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from kmtshi.models import Field,Quadrant,Classification,Candidate,Comment,jpegImages
from kmtshi.forms import CandidateForm,CommentForm,NameForm,CoordinateForm, SelectCandidatesForm
from django.utils import timezone
from django.forms import modelformset_factory
from kmtshi.plots import MagAuto_FiltersPlot,Mag_FiltersLinkPlot
from kmtshi.dates import dates_from_filename,filename_from_dates
from kmtshi.coordinates import great_circle_distance
from kmtshi.queries import simbad_query, ned_query, simbad_query_list, ned_query_list
import numpy as np
from datetime import timedelta, datetime


@login_required(login_url='/login',redirect_field_name='/')
def index(request):

    tstamp = datetime.today()
    t_ref = tstamp - timedelta(days=15)
    t_ref2 = datetime(2015,1,1,00,00)
    # Make list only of last 15 days
    field_list = Field.objects.filter(last_date__gte=t_ref).order_by('-last_date').exclude(
        subfield='N2559-1').exclude(subfield='ESO494-1').exclude(subfield='N2280-1').exclude(
        subfield='N2380-1').exclude(subfield='N2325-1').exclude(subfield='N2283-1').exclude(subfield='CGMW1-1')
    # Make list of other fields that have ANY data by not those.
    field_list_2 = Field.objects.filter(last_date__lte=t_ref).filter(last_date__gte=t_ref2).order_by('-last_date').exclude(
        subfield='N2559-1').exclude(subfield='ESO494-1').exclude(subfield='N2280-1').exclude(
        subfield='N2380-1').exclude(subfield='N2325-1').exclude(subfield='N2283-1').exclude(subfield='CGMW1-1')
    field_list_3 = Field.objects.filter(Q(subfield='N2559-1') | Q(subfield='ESO494-1') | Q(subfield='N2280-1') | Q(
        subfield='N2380-1') | Q(subfield='N2325-1') | Q(subfield='N2283-1') | Q(subfield='CGMW1-1')).order_by(
        '-last_date')

    if request.method == "POST":
        if 'name-form' in request.POST:
            name_form = NameForm(request.POST)
            if name_form.is_valid():
                name_input = name_form.cleaned_data['name']
                return redirect('search_name',sname=name_input)
            coord_form = CoordinateForm()
        if 'coord-form' in request.POST:
            coord_form = CoordinateForm(request.POST)
            if coord_form.is_valid():
                ra_input = coord_form.cleaned_data['ra']
                dec_input = coord_form.cleaned_data['dec']
                radius_input = coord_form.cleaned_data['radius']
                return redirect('search_coord',ra=ra_input,dec=dec_input,radius=radius_input)
            name_form = NameForm()
    else:
        name_form = NameForm()
        coord_form = CoordinateForm()

    context = {'field_list': field_list, 'field_list2': field_list_2, 'field_list3':field_list_3,'name_form':name_form, 'coord_form':coord_form}
    return render(request,'kmtshi/index.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def search_name(request,sname):
    #Search databased to select names that *contain* the name in the search:
    candidate_list = Candidate.objects.filter(name__icontains=sname)

    context = {'sname':sname, 'candidate_list': candidate_list}
    return render(request,'kmtshi/search_name.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def search_coord(request,ra,dec,radius):
    # Perform cone search on the candidates in the database.
    # Initial filter down to things that are close:
    ra = float(ra)
    dec = float(dec)
    radius = float(radius)
    ra_max = ra + (radius/3600.)/np.cos(dec*np.pi/180.)
    ra_min = ra - (radius/3600.)/np.cos(dec*np.pi/180.)
    dec_max = dec + (radius/3600.)
    dec_min = dec - (radius/3600.)
    candidate_list1 = Candidate.objects.filter(ra__lte=ra_max).filter(ra__gte=ra_min).filter(dec__lte=dec_max).filter(dec__gte=dec_min)

    # Use this list, and create a list that actually passes, as well as a list of the actual great_circle distance.
    distances_1 = [great_circle_distance(c.ra,c.dec,ra,dec) for c in candidate_list1]
    index1 = np.where([d < (radius/3600.) for d in distances_1])[0]
    candidate_list = [candidate_list1[int(x)] for x in index1]
    distances = ['%.3f'%(distances_1[int(x)]*3600.) for x in index1]
    combo = zip(distances,candidate_list)
    scombo = sorted(combo)

    context = {'ra':ra, 'dec':dec, 'radius':radius, 'scombo':scombo}
    return render(request,'kmtshi/search_coord.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidates(request):
    t1=Classification.objects.get(name="candidate")
    candidate_list = t1.candidate_set.all().order_by('-date_disc') #puts most recent first
    context = {'candidate_list': candidate_list}
    return render(request, 'kmtshi/candidates.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidates_field_main(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list3 = Candidate.objects.filter(classification=t1).filter(field=f1).filter(ned_flag=False).filter(simbad_flag=False).order_by('-date_disc')
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(simbad_flag=True).order_by('-date_disc')
    candidate_list2 = Candidate.objects.filter(classification=t1).filter(field=f1).filter(ned_flag=True).filter(simbad_flag=False).order_by('-date_disc')

    candidate_list4 = Candidate.objects.filter(classification=t1).filter(field=f1).filter(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__gt=0.06)
    candidate_list5= Candidate.objects.filter(classification=t1).filter(field=f1).filter(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__lt=0.06).filter(Bstddev__gt=0.02)
    candidate_list6 = Candidate.objects.filter(classification=t1).filter(field=f1).filter(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__lt=0.02).filter(Bstddev__gt=0.00)

    candidate_list7 = Candidate.objects.filter(classification=t1).filter(field=f1).exclude(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__gt=0.06).order_by('-Bstddev')
    candidate_list8 = Candidate.objects.filter(classification=t1).filter(field=f1).exclude(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__lt=0.06).filter(
        Bstddev__gt=0.02).order_by('-Bstddev')
    candidate_list9 = Candidate.objects.filter(classification=t1).filter(field=f1).exclude(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__lt=0.02).filter(
        Bstddev__gt=0.00).order_by('-Bstddev')




    num3 = len(candidate_list3)
    num2 = len(candidate_list2)
    num = len(candidate_list)

    num4 = len(candidate_list4)
    num5 = len(candidate_list5)
    num6 = len(candidate_list6)

    num7 = len(candidate_list7)
    num8 = len(candidate_list8)
    num9 = len(candidate_list9)

    context = {'field':field,  'num':num, 'num2':num2, 'num3':num3, 'num4':num4, 'num5':num5, 'num6':num6, 'num7':num7, 'num8':num8, 'num9':num9}
    return render(request, 'kmtshi/candidates_field_main.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidates_field(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(ned_flag=False).filter(simbad_flag=False).order_by('-date_disc')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field,  'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidates_field_form(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(ned_flag=False).filter(simbad_flag=False).filter(field=f1).order_by('-date_disc')
    num = len(candidate_list)

    t_junk = Classification.objects.get(name='junk')
    t_bs = Classification.objects.get(name='bad subtraction')
    t_sq = Classification.objects.get(name='unsorted star/qso')
    t_vars = Classification.objects.get(name='stellar source: variable')


    if request.method == 'POST':
        form = SelectCandidatesForm(request.POST, queryset=candidate_list)

        if form.is_valid():
            if 'junk' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_junk
                    item.save()
            elif 'bad-sub' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_bs
                    item.save()
            elif 'star-qso' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_sq
                    item.save()
            elif 'var-star' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_vars
                    item.save()

        return redirect('candidates_field_form', field=field)

    else:
        form = SelectCandidatesForm(queryset=candidate_list)


    context = {'candidate_list': candidate_list,'field':field,  'number':num, 'form': form}
    return render(request, 'kmtshi/candidates_field_form2.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidates_field_all(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).order_by('-date_disc')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field,  'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidates_field_form_all(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).order_by('-date_disc')
    num = len(candidate_list)

    t_junk = Classification.objects.get(name='junk')
    t_bs = Classification.objects.get(name='bad subtraction')
    t_sq = Classification.objects.get(name='unsorted star/qso')
    t_vars = Classification.objects.get(name='stellar source: variable')


    if request.method == 'POST':
        form = SelectCandidatesForm(request.POST, queryset=candidate_list)

        if form.is_valid():
            if 'junk' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_junk
                    item.save()
            elif 'bad-sub' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_bs
                    item.save()
            elif 'star-qso' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_sq
                    item.save()
            elif 'var-star' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_vars
                    item.save()

        return redirect('candidates_field_form_all', field=field)

    else:
        form = SelectCandidatesForm(queryset=candidate_list)


    context = {'candidate_list': candidate_list,'field':field,  'number':num, 'form': form}
    return render(request, 'kmtshi/candidates_field_form2.html', context)




@login_required(login_url='/login',redirect_field_name='/')
def candidates_field_form_var(request,field,flag):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)

    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__gt=0.06).order_by('-Bstddev')
    text = 'Bright Quiescent Sources with High Variability (stddev > 0.06 mag)'

    if flag == 'BH':
        candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(
            Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__gt=0.06).order_by('-Bstddev')
        text = 'Bright Quiescent Sources with High Variability (stddev > 0.06 mag)'
    if flag == 'BM':
        candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__lt=0.06).filter(Bstddev__gt=0.02).order_by('-Bstddev')
        text = 'Bright Quiescent Sources with Medium Variability (0.06 mag > stddev > 0.02 mag)'
    if flag == 'BL':
        candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__lt=0.02).filter(Bstddev__gt=0.00).order_by('-Bstddev')
        text = 'Bright Quiescent Sources with Low Variability (0.02 mag > stddev)'

    if flag == 'FH':
        candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).exclude(
            Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__gt=0.06).order_by('-Bstddev')
        text = 'Fainter Quiescent Sources with High Variability (stddev > 0.06 mag)'
    if flag == 'FM':
        candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).exclude(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__lt=0.06).filter(Bstddev__gt=0.02).order_by('-Bstddev')
        text = 'Fainter Quiescent Sources with Medium Variability (0.06 mag > stddev > 0.02 mag)'
    if flag == 'FL':
        candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).exclude(
        Q(Bmag__lt=16.0) | Q(Vmag__lt=16.0) | Q(Imag__lt=16.0)).filter(Bstddev__lt=0.02).filter(Bstddev__gt=0.00).order_by('-Bstddev')
        text = 'Fainter Quiescent Sources with Low Variability (0.02 mag > stddev)'



    num = len(candidate_list)

    t_junk = Classification.objects.get(name='junk')
    t_bs = Classification.objects.get(name='bad subtraction')
    t_sq = Classification.objects.get(name='unsorted star/qso')
    t_vars = Classification.objects.get(name='stellar source: variable')
    t_gen = Classification.objects.get(name='stellar source: general')

    if request.method == 'POST':
        form = SelectCandidatesForm(request.POST, queryset=candidate_list)

        if form.is_valid():
            if 'junk' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_junk
                    item.save()
            elif 'bad-sub' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_bs
                    item.save()
            elif 'star-qso' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_sq
                    item.save()
            elif 'var-star' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_vars
                    item.save()
            elif 'gen-star' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_gen
                    item.save()


        return redirect('candidates_field_form_var', field=field, flag=flag)

    else:
        form = SelectCandidatesForm(queryset=candidate_list)


    context = {'candidate_list': candidate_list,'field':field,  'number':num, 'text':text, 'form': form}
    return render(request, 'kmtshi/candidates_field_form_var.html', context)


@login_required(login_url='/login',redirect_field_name='/')
def candidates_field_simbad(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    #candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(Q(ned_flag=True) | Q(simbad_flag=True)).order_by('-date_disc')
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(simbad_flag=True).order_by('-date_disc')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field,  'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidates_field_form_simbad(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(simbad_flag=True).order_by('-date_disc')
    num = len(candidate_list)

    t_junk = Classification.objects.get(name='junk')
    t_bs = Classification.objects.get(name='bad subtraction')
    t_sq = Classification.objects.get(name='unsorted star/qso')
    t_vars = Classification.objects.get(name='stellar source: variable')

    ras = [c1.ra for c1 in candidate_list]
    decs = [c1.dec for c1 in candidate_list]
    radius = 5
    distances, types = simbad_query_list(ras, decs, radius)

    if request.method == 'POST':
        form = SelectCandidatesForm(request.POST, queryset=candidate_list)

        if form.is_valid():
            if 'junk' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_junk
                    item.save()
            elif 'bad-sub' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_bs
                    item.save()
            elif 'star-qso' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_sq
                    item.save()
            elif 'var-star' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_vars
                    item.save()

        return redirect('candidates_field_form_simbad', field=field)

    else:
        form = SelectCandidatesForm(queryset=candidate_list)


    context = {'candidate_list': candidate_list,'field':field,  'number':num, 'form': form, 'distances':distances, 'types':types}
    return render(request, 'kmtshi/candidates_field_form.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidates_field_ned(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(ned_flag=True).filter(simbad_flag=False).order_by('-date_disc')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field,  'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidates_field_form_ned(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).filter(ned_flag=True).filter(simbad_flag=False).order_by('-date_disc')
    num = len(candidate_list)

    t_junk = Classification.objects.get(name='junk')
    t_bs = Classification.objects.get(name='bad subtraction')
    t_sq = Classification.objects.get(name='unsorted star/qso')
    t_vars = Classification.objects.get(name='stellar source: variable')

    ras = [c1.ra for c1 in candidate_list]
    decs = [c1.dec for c1 in candidate_list]
    radius = 5
    distances, types = ned_query_list(ras, decs, radius)

    if request.method == 'POST':
        form = SelectCandidatesForm(request.POST, queryset=candidate_list)

        if form.is_valid():
            if 'junk' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_junk
                    item.save()
            elif 'bad-sub' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_bs
                    item.save()
            elif 'star-qso' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_sq
                    item.save()
            elif 'var-star' in request.POST:
                for item in form.cleaned_data['choices']:
                    item.classification = t_vars
                    item.save()

        return redirect('candidates_field_form_ned', field=field)

    else:
        form = SelectCandidatesForm(queryset=candidate_list)


    context = {'candidate_list': candidate_list,'field':field,  'number':num, 'form': form, 'distances':distances, 'types':types}
    return render(request, 'kmtshi/candidates_field_form.html', context)


@login_required(login_url='/login',redirect_field_name='/')
def transients(request):
    t1=Classification.objects.get(name="real transient")
    candidate_list = t1.candidate_set.all().order_by('-date_disc') #puts most recent first
    context = {'candidate_list': candidate_list}
    return render(request, 'kmtshi/candidates.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def transients_field(request,field):
    t1=Classification.objects.get(name="real transient")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).order_by('-date_disc')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field, 'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def variables(request):
    t1=Classification.objects.get(name="stellar source: variable")
    candidate_list = t1.candidate_set.all().order_by('-Bstddev') #puts most recent first
    context = {'candidate_list': candidate_list}
    return render(request, 'kmtshi/candidates.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def variables_field(request,field):
    t1=Classification.objects.get(name="stellar source: variable")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).order_by('-Bstddev')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field,  'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def galaxies(request):
    t1=Classification.objects.get(name="galaxy: variable")
    candidate_list = t1.candidate_set.all().order_by('-date_disc') #puts most recent first
    context = {'candidate_list': candidate_list}
    return render(request, 'kmtshi/candidates.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def galaxies_field(request,field):
    t1=Classification.objects.get(name="galaxy: variable")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).order_by('-date_disc')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field,  'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def candidate_date(request,field,quadrant,date):
    """The date will be in the form 170125_2045 y,m,d,_h,m"""
    f1=Field.objects.get(subfield=field)
    q1=Quadrant.objects.get(name=quadrant)
    timestamp=dates_from_filename('20'+date)
    t1 = Classification.objects.get(name="candidate")

    # Identify the candidates which are in that:
    candidate_list = Candidate.objects.filter(field=f1).filter(quadrant=q1).filter(date_disc=timestamp).filter(classification=t1)
    num = len(candidate_list)

    # Make a formset:
    # If valid update everything on the page.
    # if request.method == "POST":
    #    for candidate in cands:
    #        form = CandidateForm(request.POST, instance=candidate)
    #        if form.is_valid():
    #            candidate = form.save(commit=False)
    #            candidate.save()
    #        return redirect('candidates_field',field=field)
    #else:
    #    form = CandidateForm(instance=cands[0])

    #context = {'form': form, 'candidates': cand}
    context = {'candidate_list': candidate_list, 'field': f1, 'quad': q1, 'time': timestamp,
               'number': num,'date': date}
    return render(request, 'kmtshi/candidates_date.html', context)

@login_required(login_url='/login',redirect_field_name='/')
def detail(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    c1 = Candidate.objects.get(pk=candidate_id)
    comments_list = Comment.objects.filter(candidate=c1).order_by('-pub_date')
    png_list = jpegImages.objects.filter(candidate=c1).order_by('-obs_date')[:15]

    # Query simbad and ned at these coordinates.
    radius = 15.
    simbad_q,simbad_q2,distance = simbad_query(c1.ra,c1.dec,radius)
    ned_q,ned_q2 = ned_query(c1.ra,c1.dec,radius)

    #Create the bokeh light curve plots (ideally have set-up elsewhere):
    script,div = MagAuto_FiltersPlot(candidate_id)
    script2,div2 = Mag_FiltersLinkPlot(candidate_id)

    #Create data array for links purpose:
    date_txt = filename_from_dates(c1.date_disc)

    #Form set-up for editing the Comment field amd Modifying the Classification:
    if request.method == "POST":
        if 'comment-form' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.author = request.user
                comment.pub_date = timezone.now()
                comment.candidate = c1
                comment.save()
                return redirect('detail', candidate_id=candidate_id)
            class_form = CandidateForm(instance=candidate)
        elif 'class-form' in request.POST:
            class_form = CandidateForm(request.POST, instance=candidate)
            if class_form.is_valid():
                candidate = class_form.save(commit=False)
                candidate.save()
                return redirect('detail',candidate_id=candidate_id)
            comment_form = CommentForm()

    else:
        class_form = CandidateForm(instance=candidate)
        comment_form = CommentForm()
    context = {'class_form': class_form,'comment_form': comment_form, 'date_txt': date_txt,
               'candidate': candidate,'comments_list': comments_list,'png_list': png_list,
               'the_script': script, 'the_div': div,'the_script2': script2, 'the_div2': div2,
               'simbad_q': simbad_q,'simbad_q2':simbad_q2,'radius':radius,'distance':distance,
               'ned_q': ned_q, 'ned_q2':ned_q2}

    return render(request, 'kmtshi/detail.html',context)

@login_required(login_url='/login',redirect_field_name='/')
def classification_edit(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    field=candidate.field.subfield

    if request.method == "POST":
        form = CandidateForm(request.POST, instance=candidate)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.save()
            return redirect('candidates_field',field=field)
    else:
        form = CandidateForm(instance=candidate)
    return render(request, 'kmtshi/class_edit.html', {'form': form, 'candidate': candidate})

@login_required(login_url='/login',redirect_field_name='/')
def classification_bulkedit(request, field,quadrant,date):
    """The date will be in the form 170125_2045 y,m,d,_h,m"""
    f1=Field.objects.get(subfield=field)
    q1=Quadrant.objects.get(name=quadrant)
    timestamp=dates_from_filename('20'+date)
    t1 = Classification.objects.get(name="candidate")

    # Identify the candidates which are in that:
    candidates = Candidate.objects.filter(field=f1).filter(quadrant=q1).filter(date_disc=timestamp).filter(classification=t1)
    cand0=candidates[0]

    if request.method == "POST":
        form = CandidateForm(request.POST, instance=cand0)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.save()
            new_class = candidate.classification
            for cand in candidates:
                cand.classification = new_class
                cand.save()
            return redirect('candidates_field',field=field)
    else:
        form = CandidateForm(instance=cand0)
    context = {'form': form, 'candidate_list': candidates,'field': f1, 'quad': q1, 'time': timestamp, 'date': date}
    return render(request, 'kmtshi/class_bulkedit.html', context)
