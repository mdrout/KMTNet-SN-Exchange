from django.http import HttpResponse,Http404
from django.template import loader
from django.shortcuts import render,get_object_or_404
from kmtshi.models import Field,Quadrant,Classification,Candidate

def index(request):
    return HttpResponse("Hello, world. You're at kmtshi, the KMTNet SN Hunter's Interface.")

def candidates(request):
    t1=Classification.objects.get(name="candidate")
    candidate_list = t1.candidate_set.all().order_by('-date_disc') #puts most recent first
    context = {'candidate_list': candidate_list}
    return render(request, 'kmtshi/candidates.html', context)

def detail(request, candidate_id):
    candidate=get_object_or_404(Candidate, pk=candidate_id)
    return render(request, 'kmtshi/detail.html',{'candidate': candidate})
