#Pulisce la sessione quando l'utente esce dalla pagina di creazione di un nuovo sondaggio
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

class NewPollSessionCleaner:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        
        if 'new' in request.get_full_path() and request.GET.get('clean', None) is not None:
            if 'new' in request.session:
                del request.session['new']
            return HttpResponseRedirect(reverse('polls:create_poll'))


        if 'new' not in request.get_full_path() and 'new' in request.session:
            del request.session['new']
        
        if 'edit' not in request.get_full_path() and 'edit' in request.session:
            del request.session['edit']

        return self.get_response(request)