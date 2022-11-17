from typing import Any, Type

from django import forms
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from polls.models import Vote, Choice, Question

#Classe per la view del voto, estende la classe CreateView che è pensata per la creazione di oggetti (elementi del database)
class VoteView(CreateView):
    
    model: type[models.Model] = Vote                #il modello che vogliamo creare, vogliamo creare un voto
    fields: list[str] = ['choice']                  
    template_name: str = 'vote_create_form.html'    #setto il campo template_name al template che voglio ritornare, facendo questo viene ritornato il template corretto
                                                    #dai metodi della superclasse

    question: Question = Question()

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:  #ritorno un http response(?)
        self.__getQuestion(question_id=kwargs['id'])      #Carico la domanda nel campo question, in caso di errori sarà nullo 
        return super().get(request, *args, **kwargs)      #Chiamando il get della superclasse istanzio un form vuoto, ritorna una risposta con istanziata
                                                          #  la pagina del template con il contesto corretto, notare come si continua a passare il dizionario
                                                          #  kwargs che contiene l'id della domanda
                                                          #  super().get(...) automaticamente chiama get_context_data(...) che noi abbiamo sovrascritto
                                                          #   e che genererà il contesto che serve al template

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.__getQuestion(question_id=kwargs['id'])
        return super().post(request, *args, **kwargs)

    #override del metodo get_context_data della classe base, questo ci permette di ritornare anche la domanda al template!
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)    #prendiamo il contesto della view, a noi però serve anche la domanda!
        context['question'] = self.question             #aggiungiamo la domanda
        return context                                  #nel contesto (dizionario) abbiamo il form e la domanda

    #viene automaticamente chiamata dal get_context, facciamo l'override perchè dobbiamo generare il form dal database
    def get_form(self, form_class: Type[forms.BaseModelForm] = None):
        form = super().get_form(form_class)                            #prendiamo la classe Form usata nella view (dovrebbe essere vuoto)
        form.fields['choice'] = forms.ModelChoiceField(                #ridefiniamo "choice" e gli asseggnamo come valore un form di tipo checkbox generato dal database
            queryset=Choice.objects.filter(question=self.question),    
            widget=forms.RadioSelect,                                  #specifichiamo che vogliamo un radio button
            label='Opzioni'
        )
        return form

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        form.instance.question = self.question
        form.save()
        return render(self.request, 'vote_success.html', {'question_id': self.question.id})

    def get_success_url(self) -> str:
        return reverse('polls:successfull_vote_insertion')

    #metodo per recuperare la domanda dal database, gli passo l'id della domanda
    def __getQuestion(self, question_id):
        try:
            self.question = Question.objects.get(id=question_id) #il campo question diventa l'oggetto Question del database con id = question_id
            if  self.question.choice_set.count() == 0:           #controllo per vedere se la domanda ha risposte associate, se non ne ha tratto la domanda come se non esistesse
                self.question = None                             #setto a None
        except ObjectDoesNotExist:
            self.question = None                                 #setto a None
