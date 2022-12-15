from .poll_editor import poll_editor_main, poll_editor_summary_and_additional_options
from polls.models import Poll
from django.shortcuts import render

#Legge dalla sessione il numero di pagina e quindi mostra la prima o la seconda pagina della creazione del sondaggio
def edit_poll(request, id):
    print(id)
    if len(Poll.objects.get(id=id).preference_set.all())>0:
        return render(request, '403.html')
    if 'edit_poll_page_index' not in request.session:
        request.session['edit_poll_page_index']=1
    if request.session['edit_poll_page_index']==1:
        return poll_editor_main(request,poll=Poll.objects.get(id=id))
    else:
        return poll_editor_summary_and_additional_options(request,poll=Poll.objects.get(id=id))