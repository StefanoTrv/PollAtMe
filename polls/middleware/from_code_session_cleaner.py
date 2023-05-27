#Pulisce la sessione quando l'utente esce dalla pagina di creazione di un nuovo sondaggio
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

VOTE_PREFIX = "vote"

class FromCodeSessionCleaner:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        
        #se nell'url non c'è vote possiamo cancellare il campo della session
        if VOTE_PREFIX not in request.get_full_path():
            if 'from_code' in request.session:
                del request.session['from_code']

        response = self.get_response(request)

        if VOTE_PREFIX in request.get_full_path() and 'preference_id' in request.session:
            if 'from_code' in request.session:
                del request.session['from_code']

        return response