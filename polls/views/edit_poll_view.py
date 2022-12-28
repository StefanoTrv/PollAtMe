from django.core.exceptions import PermissionDenied

from polls.models import Poll

from polls.services import SearchPollService

from .poll_editor import (poll_editor_main,
                          poll_editor_summary_and_additional_options)


#Legge dalla sessione il numero di pagina e quindi mostra la prima o la seconda pagina della creazione del sondaggio
def edit_poll(request, id):
    print(id)
    
    poll = SearchPollService().search_by_id(id)

    if poll.is_active():
        raise PermissionDenied("Non è possibile modificare il sondaggio perché è in corso la votazione")
    
    if poll.is_ended():
        raise PermissionDenied("Questo sondaggio è concluso e non può essere modificato")

    if 'edit_poll_page_index' not in request.session:
        request.session['edit_poll_page_index']=1
    if request.session['edit_poll_page_index']==1:
        return poll_editor_main(request,poll=poll)
    else:
        return poll_editor_summary_and_additional_options(request,poll=poll)