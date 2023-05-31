from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

NEW_PREFIX = "new"
EDIT_PREFIX = "edit"

class NewPollSessionCleaner:
    """Cleans the session when a user goes out from the creation page of a poll"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        
        if NEW_PREFIX in request.get_full_path() and request.GET.get('clean', None) is not None:
            if 'create' in request.session:
                del request.session['create']
            return HttpResponseRedirect(reverse('polls:create_poll'))

        if NEW_PREFIX not in request.get_full_path() and NEW_PREFIX in request.session:
            del request.session[NEW_PREFIX]
        
        if EDIT_PREFIX not in request.get_full_path() and EDIT_PREFIX in request.session:
            del request.session[EDIT_PREFIX]

        return self.get_response(request)