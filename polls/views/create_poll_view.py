from django.http import HttpRequest

from .poll_editor import poll_editor_main, poll_editor_summary_and_additional_options

#Legge dalla sessione il numero di pagina e quindi mostra la prima o la seconda pagina della creazione del sondaggio
def create_poll(request: HttpRequest):
    if 'new_poll_page_index' not in request.session:
        request.session['new_poll_page_index'] = 1
    if request.session['new_poll_page_index'] == 1:
        return poll_editor_main(request)
    else:
        return poll_editor_summary_and_additional_options(request)