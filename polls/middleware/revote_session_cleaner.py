#Pulisce la sessione relativa al rivoto quando l'utente esce dalle pagine di voto
from django.http import HttpRequest

class RevoteSessionCleaner:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if 'preference_id' in request.session and 'vote_single_preference' not in request.get_full_path() and 'vote_majority_judgment' not in request.get_full_path():
            del request.session['preference_id']
        return self.get_response(request)