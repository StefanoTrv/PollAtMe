from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from polls.forms import CreatePollFormMain, CreatePollAdditionalOptions
from polls.services import add_single_preference_poll, add_majority_judgment_poll

#Legge dalla sessione il numero di pagina e quindi mostra la prima o la seconda pagina della creazione del sondaggio
def create_poll(request):
    if 'new_poll_page_index' not in request.session:
        request.session['new_poll_page_index']=1
    if request.session['new_poll_page_index']==1:
        return _create_poll_main(request)
    else:
        return _create_poll_summary_and_additional_options(request)

# View per la pagina principale della creazione del sondaggio, in cui si scelgono i parametri fondamentali.
def _create_poll_main(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollFormMain(request.POST, count=request.POST.get('hidden_alternative_count'))
        # check whether it's valid:
        if form.is_valid():
            alternative_count=form.cleaned_data['hidden_alternative_count']
            request.session['new_poll_title']=form.cleaned_data['poll_title']
            request.session['new_poll_text']=form.cleaned_data['poll_text']
            request.session['new_poll_alternative_count']=alternative_count
            alternatives=[]
            for i in range(1,alternative_count+1):
                alternatives.append(form.cleaned_data['alternative'+str(i)])
            request.session['new_poll_alternatives']=alternatives
            request.session['new_poll_type']=form.cleaned_data['poll_type']
            request.session['new_poll_page_index']=2
            return HttpResponseRedirect(reverse('polls:create_poll')) #redirect alla stessa pagina per forzare il caricamento della prossima schermata
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreatePollFormMain()

    return render(request, 'create_poll/main_page.html', {'form': form})

#View per la seconda pagina della creazione di un nuovo sondaggio, che mostra i dati inseriti prima e consente di scegliere opzioni aggiuntive secondarie.
def _create_poll_summary_and_additional_options(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollAdditionalOptions(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if request.session['new_poll_type']=='Preferenza singola':
                add_single_preference_poll(request.session['new_poll_title'],request.session['new_poll_text'],request.session['new_poll_alternatives'])
            elif request.session['new_poll_type']=='Giudizio maggioritario':
                add_majority_judgment_poll(request.session['new_poll_title'],request.session['new_poll_text'],request.session['new_poll_alternatives'])
            return render(request, 'create_poll_success.html')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreatePollAdditionalOptions()

    return render(request, 'create_poll/summary_and_additional_options_page.html', {'form': form,  'title': request.session['new_poll_title'],  'text': request.session['new_poll_text'],  'alternatives': request.session['new_poll_alternatives']})