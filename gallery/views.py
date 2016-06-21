from django.http import Http404, HttpResponse


def photo(request, photo_id=None):
    return HttpResponse('1')


def tag(request, tag_id=None):
    return HttpResponse('2')