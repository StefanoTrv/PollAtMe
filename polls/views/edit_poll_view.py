from polls.services import SearchPollService

from .poll_editor import (poll_editor_main,
                          poll_editor_summary_and_additional_options, can_edit_poll)


#Legge dalla sessione il numero di pagina e quindi mostra la prima o la seconda pagina della creazione del sondaggio
def edit_poll(request, id):
    print(id)
    
    poll = SearchPollService().search_by_id(id)

    can_edit_poll(poll)

    if 'edit_poll_page_index' not in request.session:
        request.session['edit_poll_page_index']=1
    if request.session['edit_poll_page_index']==1:
        return poll_editor_main(request,poll=poll)
    else:
        return poll_editor_summary_and_additional_options(request,poll=poll)