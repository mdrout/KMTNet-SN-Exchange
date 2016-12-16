from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at kmtshi, the KMTNet SN Hunter's Interface")
