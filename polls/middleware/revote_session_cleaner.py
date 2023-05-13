#Pulisce la sessione relativa al rivoto quando l'utente esce dalle pagine di voto
from django.http import HttpRequest

class RevoteSessionCleaner:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if 'preference_id' in request.session and 'vote/singlepreference' not in request.get_full_path() and 'vote/majorityjudgment' not in request.get_full_path() and 'vote/shultze' not in request.get_full_path() and 'help/majorityjudgment' not in request.get_full_path() and 'help/schulze_method' not in request.get_full_path():
            del request.session['preference_id']
        if 'alternative_sp' in request.session and 'vote/majorityjudgment' not in request.get_full_path() and 'help/majorityjudgment' not in request.get_full_path() and 'help/schulze_method/' not in request.get_full_path():
            del request.session['alternative_sp']
        return self.get_response(request)