from django.http import HttpResponse,Http404
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from kmtshi.models import Field,Quadrant,Classification,Candidate,Comment,PngImages
from kmtshi.forms import CandidateForm,CommentForm
from django.utils import timezone
import glob
from kmtshi.plots import MagAuto_FiltersPlot,Mag_FiltersLinkPlot

def index(request):
    return HttpResponse("Hello, world. You're at kmtshi, the KMTNet SN Hunter's Interface.")


def candidates(request):
    t1=Classification.objects.get(name="candidate")
    candidate_list = t1.candidate_set.all().order_by('-date_disc') #puts most recent first
    context = {'candidate_list': candidate_list}
    return render(request, 'kmtshi/candidates.html', context)

def candidates_field(request,field):
    t1=Classification.objects.get(name="candidate")
    f1=Field.objects.get(subfield=field)
    candidate_list = Candidate.objects.filter(classification=t1).filter(field=f1).order_by('-date_disc')
    context = {'candidate_list': candidate_list,'field':field}
    return render(request, 'kmtshi/candidates_field.html', context)

def detail(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    c1 = Candidate.objects.get(pk=candidate_id)
    comments_list = Comment.objects.filter(candidate=c1).order_by('-pub_date')
    png_list = PngImages.objects.filter(candidate=c1).order_by('-obs_date')[:15]

    #Create the bokeh light curve plots (ideally have set-up elsewhere):
    script,div = MagAuto_FiltersPlot(candidate_id)
    script2,div2 = Mag_FiltersLinkPlot(candidate_id)

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
    context = {'class_form': class_form,'comment_form': comment_form,
               'candidate': candidate,'comments_list': comments_list,'png_list': png_list,
               'the_script': script, 'the_div': div,'the_script2': script2, 'the_div2': div2}

    return render(request, 'kmtshi/detail.html',context)


def classification_edit(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    if request.method == "POST":
        form = CandidateForm(request.POST, instance=candidate)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.save()
            return redirect('candidates')
    else:
        form = CandidateForm(instance=candidate)
    return render(request, 'kmtshi/class_edit.html', {'form': form, 'candidate': candidate})
