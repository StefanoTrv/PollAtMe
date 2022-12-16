#Pulisce la sessione quando l'utente esce dalla pagina di creazione di un nuovo sondaggio
class NewPollSessionCleaner:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'create_poll' not in request.get_full_path():
            if 'new_poll_title' in request.session:
                del request.session['new_poll_title']
            if 'new_poll_text' in request.session:
                del request.session['new_poll_text']
            if 'new_poll_alternative_count' in request.session:
                del request.session['new_poll_alternative_count']
            if 'new_poll_alternatives' in request.session:
                del request.session['new_poll_alternatives']
            if 'new_poll_page_index' in request.session:
                del request.session['new_poll_page_index']
            if 'new_poll_type' in request.session:
                del request.session['new_poll_type']
        
        if 'edit_poll' not in request.get_full_path():
            if 'edit_poll_title' in request.session:
                del request.session['edit_poll_title']
            if 'edit_poll_text' in request.session:
                del request.session['edit_poll_text']
            if 'edit_poll_alternative_count' in request.session:
                del request.session['edit_poll_alternative_count']
            if 'edit_poll_alternatives' in request.session:
                del request.session['edit_poll_alternatives']
            if 'edit_poll_page_index' in request.session:
                del request.session['edit_poll_page_index']
            if 'edit_poll_type' in request.session:
                del request.session['edit_poll_type']

        response = self.get_response(request)

        return response