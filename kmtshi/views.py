from django.http import HttpResponse,Http404
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from kmtshi.models import Field,Quadrant,Classification,Candidate,Comment,jpegImages
from kmtshi.forms import CandidateForm,CommentForm,NameForm,CoordinateForm
from django.utils import timezone
from django.forms import modelformset_factory
from kmtshi.plots import MagAuto_FiltersPlot,Mag_FiltersLinkPlot
from kmtshi.dates import dates_from_filename,filename_from_dates
from kmtshi.coordinates import great_circle_distance
import numpy as np

def index(request):
    field_list = Field.objects.all().order_by('-last_date')

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

    context = {'field_list': field_list, 'name_form':name_form, 'coord_form':coord_form}
    return render(request,'kmtshi/index.html', context)

def search_name(request,sname):
    #Search databased to select names that *contain* the name in the search:
    candidate_list = Candidate.objects.filter(name__icontains=sname)

    context = {'sname':sname, 'candidate_list': candidate_list}
    return render(request,'kmtshi/search_name.html', context)

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

    context = {'ra':ra, 'dec':dec, 'radius':radius, 'candidate_list':candidate_list,'distances':distances}
    return render(request,'kmtshi/search_coord.html', context)

def candidates(request):
    t1=Classification.objects.get(name="candidate")
    candidate_list = t1.candidate_set.all().order_by('-date_disc') #puts most recent first
    context = {'candidate_list': candidate_list}
    return render(request, 'kmtshi/candidates.html', context)


def candidates_field(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).order_by('-date_disc')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field,  'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)

def transients(request):
    t1=Classification.objects.get(name="real transient")
    candidate_list = t1.candidate_set.all().order_by('-date_disc') #puts most recent first
    context = {'candidate_list': candidate_list}
    return render(request, 'kmtshi/candidates.html', context)


def transients_field(request,field):
    t1=Classification.objects.get(name="real transient")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).order_by('-date_disc')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field, 'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)

def variables(request):
    t1=Classification.objects.get(name="stellar source: variable")
    candidate_list = t1.candidate_set.all().order_by('-date_disc') #puts most recent first
    context = {'candidate_list': candidate_list}
    return render(request, 'kmtshi/candidates.html', context)


def variables_field(request,field):
    t1=Classification.objects.get(name="stellar source: variable")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).order_by('-date_disc')
    num = len(candidate_list)
    context = {'candidate_list': candidate_list,'field':field,  'number':num}
    return render(request, 'kmtshi/candidates_field.html', context)


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


def detail(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    c1 = Candidate.objects.get(pk=candidate_id)
    comments_list = Comment.objects.filter(candidate=c1).order_by('-pub_date')
    png_list = jpegImages.objects.filter(candidate=c1).order_by('-obs_date')[:15]

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
               'the_script': script, 'the_div': div,'the_script2': script2, 'the_div2': div2}

    return render(request, 'kmtshi/detail.html',context)


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
