from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import render

from polls.forms import CreatePollFormMain, CreatePollAdditionalOptions
from polls.services import add_single_preference_poll, add_majority_judgment_poll, update_poll

# View per la pagina principale della creazione o modifica del sondaggio, in cui si scelgono i parametri fondamentali.
# Il parametro poll è specificato quando si intende modificare un sondaggio esistente.
def poll_editor_main(request: HttpRequest, poll = None):
    if poll==None:
        session_prefix = "new"
    else:
        session_prefix = "edit"
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollFormMain(request.POST, count = request.POST.get('hidden_alternative_count'))
        # check whether it's valid:
        if form.is_valid():
            alternative_count = form.cleaned_data['hidden_alternative_count']
            request.session[f'{session_prefix}_poll_title'] = form.cleaned_data['poll_title']
            request.session[f'{session_prefix}_poll_text'] = form.cleaned_data['poll_text']
            request.session[f'{session_prefix}_poll_alternative_count'] = alternative_count
            alternatives = []
            for i in range(1, alternative_count + 1):
                alternatives.append(form.cleaned_data[f'alternative{i}'])
            request.session[f'{session_prefix}_poll_alternatives'] = alternatives
            request.session[f'{session_prefix}_poll_type'] = form.cleaned_data['poll_type']
            request.session[f'{session_prefix}_poll_page_index'] = 2
            return HttpResponseRedirect(request.get_full_path()) #redirect alla stessa pagina per forzare il caricamento della prossima schermata
        else: #crea un nuovo form con gli stessi dati, in modo da eliminare definitivamente i campi cancellati
            alternatives = []
            for i in range(1, form.cleaned_data['hidden_alternative_count'] + 1):
                alternatives.append(form.cleaned_data['alternative'+str(i)])
            errors = form.errors #brutto modo per far riapparire gli errori nel form ricreato
            form=CreatePollFormMain(
                poll_title=form.cleaned_data.get('poll_title',''),
                poll_text=form.cleaned_data.get('poll_text',''),
                poll_type=form.cleaned_data['poll_type'],
                alternatives=alternatives)
            form._errors=errors # type: ignore
    # if a GET (or any other method) we'll create a blank form
    else:
        if poll == None:#vuoto se stiamo creando un nuovo sondaggio
            form = CreatePollFormMain()
        else:#se stiamo modificando un sondaggio esistente, precompiliamo i campi
            form=CreatePollFormMain(poll=poll)

    return render(request, 'create_poll/main_page.html', {'form': form})

#View per la seconda pagina della creazione o modifica di un sondaggio, che mostra i dati inseriti prima e consente di scegliere opzioni aggiuntive secondarie.
# Il parametro poll è specificato quando si intende modificare un sondaggio esistente.
def poll_editor_summary_and_additional_options(request, poll = None):
    if poll==None:
        session_prefix = "new"
    else:
        session_prefix = "edit"
    #richiesta di tornare alla pagina precedente
    if request.method == 'POST' and 'go_back' in request.POST:
        form=CreatePollFormMain(
            poll_title  = request.session[f'{session_prefix}_poll_title'],
            poll_text   = request.session[f'{session_prefix}_poll_text'],
            poll_type   = request.session[f'{session_prefix}_poll_type'],
            alternatives= request.session[f'{session_prefix}_poll_alternatives']
            )
        request.session[f'{session_prefix}_poll_page_index']=1
        return render(request, 'create_poll/main_page.html', {'form': form}) #mostra la pagina precedente
    #richiesta di salvare il sondaggio
    elif request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollAdditionalOptions(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if poll != None and poll.get_type()==request.session[f'{session_prefix}_poll_type']:#aggiornamento senza cambiare tipo di poll
                update_poll(
                    poll,
                    request.session[f'{session_prefix}_poll_title'],
                    request.session[f'{session_prefix}_poll_text'],
                    request.session[f'{session_prefix}_poll_alternatives'],
                    form.cleaned_data['start_time'],
                    form.cleaned_data['end_time']
                )
                return render(request, 'update_poll_success.html')
            elif request.session[f'{session_prefix}_poll_type'] == 'Preferenza singola':#creazione o update con cambio di tipo
                if poll!=None:#cancello il poll del vecchio tipo
                    poll.delete()
                add_single_preference_poll(
                    request.session[f'{session_prefix}_poll_title'],
                    request.session[f'{session_prefix}_poll_text'],
                    request.session[f'{session_prefix}_poll_alternatives'],
                    form.cleaned_data['start_time'],
                    form.cleaned_data['end_time']
                )
            elif request.session[f'{session_prefix}_poll_type'] == 'Giudizio maggioritario':#creazione o update con cambio di tipo
                if poll!=None:#cancello il poll del vecchio tipo
                    poll.delete()
                add_majority_judgment_poll(
                    request.session[f'{session_prefix}_poll_title'],
                    request.session[f'{session_prefix}_poll_text'],
                    request.session[f'{session_prefix}_poll_alternatives'],
                    form.cleaned_data['start_time'],
                    form.cleaned_data['end_time']
                )
            return render(request, 'create_poll_success.html')

    # if a GET (or any other method) we'll create a form
    else:
        if poll == None:
            form = CreatePollAdditionalOptions()
        else:
            form = CreatePollAdditionalOptions(poll=poll)

    return render(request, 'create_poll/summary_and_additional_options_page.html', {
        'form': form,
        'type': request.session[f'{session_prefix}_poll_type'],
        'title': request.session[f'{session_prefix}_poll_title'],
        'text': request.session[f'{session_prefix}_poll_text'],
        'alternatives': request.session[f'{session_prefix}_poll_alternatives']
    })