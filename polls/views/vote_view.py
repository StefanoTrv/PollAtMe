from typing import Any, Type

from django import forms
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.shortcuts import render

from polls.models import SinglePreference, Alternative, Poll
from polls.services import SearchPollService
from polls.exceptions import PollWithoutAlternativesException
from django.core.exceptions import ObjectDoesNotExist

#Classe per la view del voto, estende la classe CreateView che è pensata per la creazione di oggetti (elementi del database)
class VoteView(CreateView):
    
    POLL_DOES_NOT_EXISTS_MSG = "Il sondaggio ricercato non esiste"
    NO_ALTERNATIVES_POLL_MSG = "Il sondaggio ricercato non ha opzioni di risposta"

    model: type[models.Model] = SinglePreference                #il modello che vogliamo creare, vogliamo creare una preferenza
    fields: list[str] = ['alternative']                  
    template_name: str = 'vote_create_form.html'    #setto il campo template_name al template che voglio ritornare, facendo questo viene ritornato il template corretto
                                                    #dai metodi della superclasse

    def __init__(self, **kwargs: Any) -> None:
        self.__poll: Poll = Poll()
        self.__poll_service: SearchPollService = SearchPollService()
        self.__error: str
        super().__init__(**kwargs)

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:  #ritorno un http response(?)
        self.__get_poll(kwargs['id'])                     #Carico la domanda nel campo poll
        return super().get(request, *args, **kwargs)      #Chiamando il get della superclasse istanzio un form vuoto, ritorna una risposta con istanziata
                                                          #  la pagina del template con il contesto corretto, notare come si continua a passare il dizionario
                                                          #  kwargs che contiene l'id della domanda
                                                          #  super().get(...) automaticamente chiama get_context_data(...) che noi abbiamo sovrascritto
                                                          #   e che genererà il contesto che serve al template

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.__get_poll(kwargs['id'])
        return super().post(request, *args, **kwargs)

    #override del metodo get_context_data della classe base, questo ci permette di ritornare anche la domanda al template!
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)    #prendiamo il contesto della view, a noi però serve anche la domanda!
        context['poll'] = self.__poll                     #aggiungiamo la domanda
        context['error'] = self.__error
        return context                                  #nel contesto (dizionario) abbiamo il form e la domanda

    #viene automaticamente chiamata dal get_context, facciamo l'override perchè dobbiamo generare il form dal database
    def get_form(self, form_class: Type[forms.BaseModelForm] = None):
        form = super().get_form(form_class)                            #prendiamo la classe Form usata nella view (dovrebbe essere vuoto)
        form.fields['alternative'] = forms.ModelChoiceField(                #ridefiniamo "alternative" e gli assegnamo come valore un form di tipo checkbox generato dal database
            queryset=Alternative.objects.filter(poll=self.__poll),    
            widget=forms.RadioSelect,                                  #specifichiamo che vogliamo un radio button
            label='Opzioni'
        )
        return form

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        form.instance.poll = self.__poll
        form.save()
        return render(self.request, 'vote_success.html', {'poll_id': self.__poll.id})

    def get_success_url(self) -> str:
        return reverse('polls:successfull_vote_insertion')

    def __get_poll(self, poll_id):
        try:
            self.__poll = self.__poll_service.search_by_id(poll_id)
        except ObjectDoesNotExist:
            self.__error = self.POLL_DOES_NOT_EXISTS_MSG
            self.__poll = None
        except PollWithoutAlternativesException:
            self.__error = self.NO_ALTERNATIVES_POLL_MSG
            self.__poll = None
        else:
            self.__error = None
