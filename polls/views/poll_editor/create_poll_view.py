from django.http import HttpRequest

from polls.services import SearchPollService

from .poll_editor_view import PollSessionTemp, can_edit_poll


#Legge dalla sessione il numero di pagina e quindi mostra la prima o la seconda pagina della creazione del sondaggio
def create_poll(request: HttpRequest):
    return __redirect_to_page('new', request)

def edit_poll(request: HttpRequest, id):
    poll = SearchPollService().search_by_id(id)
    can_edit_poll(poll)
    return __redirect_to_page('edit', request, poll)
    

def __redirect_to_page(action: str, request: HttpRequest, poll = None):
    session_dict: dict = request.session.get(action, None)
    if session_dict is None:
        session = PollSessionTemp()
        request.session[action] = session.__dict__
    else:
        session = PollSessionTemp(**session_dict)
    return session.get_page_by_current_index(request, poll)
