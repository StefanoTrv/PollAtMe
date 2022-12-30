from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from polls.forms import CreatePollAdditionalOptions, CreatePollFormMain
from polls.models import Poll
from polls.services import (add_majority_judgment_poll,
                            add_single_preference_poll, update_poll)


class PollSessionTemp:    
    def __init__(self, **kwargs):
        self.hidden_alternative_count = kwargs.get('hidden_alternative_count', '')
        self.poll_title = kwargs.get('poll_title', '')
        self.poll_text = kwargs.get('poll_text', '')
        self.poll_alternatives = kwargs.get('poll_alternatives', alternatives_as_list(**kwargs))
        self.poll_type = kwargs.get('poll_type', '')
        self.poll_page_index = kwargs.get('poll_page_index', 1)
    
    def get_page_by_current_index(self, request: HttpRequest, poll=None):
        if self.poll_page_index == 1:
            return poll_editor_main(request=request, poll=poll)
        else:
            return poll_editor_summary_and_additional_options(request=request, poll=poll)

def can_edit_poll(poll: Poll):
    if poll.is_active():
        raise PermissionDenied("Non è possibile modificare il sondaggio perché è in corso la votazione")
    
    if poll.is_ended():
        raise PermissionDenied("Questo sondaggio è concluso e non può essere modificato")

def alternatives_as_list(**kwargs):
    return [
        field for k, field in kwargs.items() if k.startswith('alternative')
    ]

# View per la pagina principale della creazione o modifica del sondaggio, in cui si scelgono i parametri fondamentali.
# Il parametro poll è specificato quando si intende modificare un sondaggio esistente.
def poll_editor_main(request: HttpRequest, poll = None):
    action = "new" if poll is None else "edit"

    # if this is a POST request we need to process the form data
    errors = None
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollFormMain(request.POST, count = request.POST.get('hidden_alternative_count'))
        # check whether it's valid:
        if form.is_valid():
            session = PollSessionTemp(**form.cleaned_data, poll_page_index=2)
            request.session[action] = session.__dict__
            return HttpResponseRedirect(request.get_full_path()) #redirect alla stessa pagina per forzare il caricamento della prossima schermata
        else:
            # renderizza un nuovo form con gli stessi dati, ma con il numero corretto di alternative (problema del form bounded)
            errors = form.errors
            form=CreatePollFormMain(
                poll_title=form.cleaned_data.get('poll_title',''),
                poll_text=form.cleaned_data.get('poll_text',''),
                poll_type=form.cleaned_data['poll_type'],
                alternatives=alternatives_as_list(**form.cleaned_data)
            )
    else:
        if poll == None:#vuoto se stiamo creando un nuovo sondaggio
            form = CreatePollFormMain()
        else:#se stiamo modificando un sondaggio esistente, precompiliamo i campi
            form=CreatePollFormMain(poll=poll)

    return render(request, 'create_poll/main_page.html', {'form': form, 'errors': errors})

#View per la seconda pagina della creazione o modifica di un sondaggio, che mostra i dati inseriti prima e consente di scegliere opzioni aggiuntive secondarie.
# Il parametro poll è specificato quando si intende modificare un sondaggio esistente.
def poll_editor_summary_and_additional_options(request: HttpRequest, poll: Poll|None = None):
    action = "new" if poll is None else "edit"
    session: PollSessionTemp = PollSessionTemp(**request.session[action])

    #richiesta di tornare alla pagina precedente
    if request.method == 'POST' and 'go_back' in request.POST:
        form = CreatePollFormMain(
            poll_title  = session.poll_title,
            poll_text   = session.poll_text,
            poll_type   = session.poll_type,
            alternatives= session.poll_alternatives
            )
        session.poll_page_index = 1
        request.session[action] = session.__dict__
        return render(request, 'create_poll/main_page.html', {'form': form}) #mostra la pagina precedente
    #richiesta di salvare il sondaggio
    elif request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollAdditionalOptions(request.POST) # type: ignore
        # check whether it's valid:
        if form.is_valid():
            if poll is not None and poll.get_type() == session.poll_type :#aggiornamento senza cambiare tipo di poll
                can_edit_poll(poll)
                update_poll(
                    poll,
                    session.poll_title,
                    session.poll_text,
                    session.poll_alternatives,
                    form.cleaned_data['start_time'],
                    form.cleaned_data['end_time']
                )
            elif session.poll_type == 'Preferenza singola':#creazione o update con cambio di tipo
                if poll is not None: #cancello il poll del vecchio tipo
                    can_edit_poll(poll)
                    poll.delete()

                add_single_preference_poll(
                    session.poll_title,
                    session.poll_text,
                    session.poll_alternatives,
                    form.cleaned_data['start_time'],
                    form.cleaned_data['end_time']
                )
            elif session.poll_type == 'Giudizio maggioritario':#creazione o update con cambio di tipo
                if poll is not None:#cancello il poll del vecchio tipo
                    can_edit_poll(poll)
                    poll.delete()
                
                add_majority_judgment_poll(
                    session.poll_title,
                    session.poll_text,
                    session.poll_alternatives,
                    form.cleaned_data['start_time'],
                    form.cleaned_data['end_time']
                )

            if poll is not None:
                return render(request, 'update_poll_success.html')
            else:
                return render(request, 'create_poll_success.html')

    # if a GET (or any other method) we'll create a form
    else:
        if poll == None:
            form = CreatePollAdditionalOptions() # type: ignore
        else:
            form = CreatePollAdditionalOptions(poll=poll) # type: ignore

    return render(request, 'create_poll/summary_and_additional_options_page.html', {
        'form': form,
        'type': session.poll_type,
        'title': session.poll_title,
        'text': session.poll_text,
        'alternatives': session.poll_alternatives
    })