from django.http import HttpRequest

class RevoteSessionCleaner:
    """Cleans the session when a user goes out from a vote page"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __prefixs_not_in_path(self, request: HttpRequest, prefixs: list):
        for prefix in prefixs:
            if prefix in request.get_full_path():
                return False
        return True

    def __call__(self, request: HttpRequest):
        if 'preference_id' in request.session and self.__prefixs_not_in_path(request, [
            'vote', 
            'help/majorityjudgment',
            'help/schulze_method/'
            ]):
            del request.session['preference_id']

        delete_vote_from_session = self.__prefixs_not_in_path(request, [
            'vote/majorityjudgment', 
            'help/majorityjudgment',
            'help/schulze_method/'
        ])

        if 'alternative_sp' in request.session and delete_vote_from_session:
            del request.session['alternative_sp']
        
        if 'sequence_shultze' in request.session and delete_vote_from_session:
            del request.session['sequence_shultze']

        if 'revote_type' in request.session and delete_vote_from_session:
            del request.session['revote_type']

        return self.get_response(request)