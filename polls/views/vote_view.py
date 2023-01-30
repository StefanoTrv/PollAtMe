import random
from typing import Any, Callable, Optional, Type

from django import forms, http
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import CreateView
from django.db.models.query import QuerySet
from django.urls import reverse

from polls.exceptions import PollWithoutAlternativesException
from polls.forms import (MajorityPreferenceFormSet,
                         SinglePreferenceForm)
from polls.models import MajorityOpinionJudgement, MajorityPreference, Poll
from polls.models.preference import SinglePreference
from polls.services import SearchPollService

#se si accede alla pagina di voto generica, si viene reindirizzati alla pagina di voto del metodo principale
def vote_redirect_view(request, id):
    poll = SearchPollService().search_by_id(id)
    if poll.get_type()=="Preferenza singola":
        return redirect(reverse('polls:vote_single_preference', args=[id]))
    else:
        return redirect(reverse('polls:vote_MJ', args=[id]))


class _VotingView(CreateView):
    """
    Class view (de facto astratta) che incorpora ciò che hanno in comune le diverse pagine di voto
    """
    poll: Poll
    voteType: str
    alternatives: QuerySet

    def dispatch(self, request, *args, **kwargs):
        """
        Questo metodo viene invocato quando viene fatta una richiesta
        HTTP (di qualunque tipo).
        """
        try:
            self.poll = SearchPollService().search_by_id(kwargs['id'])
            self.alternatives = self.poll.alternative_set.all()
            if not self.poll.is_active():
                raise PermissionDenied('Non è possibile votare questo sondaggio')
        except PollWithoutAlternativesException:
            raise http.Http404("Il sondaggio ricercato non ha opzioni di risposta")
            
        #controllo che, se è un metodo di voto alternativo, l'ID della preferenza sintetica sia presente e corretto
        if self.poll.get_type()!=self.voteType:
            if 'preference_id' not in request.session:
                raise PermissionDenied('Il voto con metodi alternativi è concesso solo durante il rivoto')
            syntethic_preference = SinglePreference.objects.get(id=request.session['preference_id'])
            if syntethic_preference.poll!=self.poll:
                raise PermissionDenied('Il voto con metodi alternativi è concesso solo durante il rivoto\n(Dettagli dell\'errore: la preferenza sintetica è riferita ad un poll diverso)')
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Metodo per l'inserimento delle variabili dalla view al template
        """
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        return context


class VoteSinglePreferenceView(_VotingView):

    form_class: Optional[Type[forms.BaseForm]] = SinglePreferenceForm
    template_name: str = 'polls/vote/vote_SP.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.voteType="Preferenza singola"

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Inizializzo gli argomenti per il form, in questo caso la poll
        da cui estrarre le opzioni
        """
        kwargs = super().get_form_kwargs()
        kwargs['poll'] = self.poll
        return kwargs

    def form_valid(self, form: forms.BaseModelForm) -> http.HttpResponse:
        form.instance.poll = self.poll
        new_preference = form.save()

        #crea voto sintetico
        synthetic_preference = MajorityPreference()
        synthetic_preference.poll=self.poll
        synthetic_preference.synthetic=True
        synthetic_preference.save()
        for alternative in self.alternatives:
            moj = MajorityOpinionJudgement()
            moj.alternative=alternative
            moj.preference=synthetic_preference
            if alternative == new_preference.alternative:
                moj.grade=5 # type: ignore
            else:
                moj.grade=1 # type: ignore
            moj.save()
            synthetic_preference.majorityopinionjudgement_set.add(moj) # type: ignore
        synthetic_preference.save()#serve? Forse no

        self.request.session['preference_id']=synthetic_preference.id

        return render(self.request, 'polls/vote_success.html', {'poll_id': self.poll.id})


class VoteMajorityJudgmentView(_VotingView):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
    template_name: str = 'polls/vote/vote_GM.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.voteType="Giudizio maggioritario"

    def form_valid(self, form: forms.BaseInlineFormSet) -> http.HttpResponse:
        preference = MajorityPreference(poll = self.poll)
        preference.save()

        instance: MajorityOpinionJudgement
        for instance in form.save(commit=False):
            instance.preference = preference
            instance.save()
        
        #crea voto sintetico
        synthetic_preference = SinglePreference()
        synthetic_preference.poll=self.poll
        synthetic_preference.synthetic=True
        best_grade = max([opinion.grade for opinion in preference.majorityopinionjudgement_set.all()])
        top_options = [opinion.alternative for opinion in preference.majorityopinionjudgement_set.all() if opinion.grade==best_grade]
        synthetic_preference.alternative=top_options[random.randint(0,len(top_options)-1)]#se ci sono più preferenze con lo stesso voto, ne sceglie una a caso
        synthetic_preference.save()

        self.request.session['preference_id']=synthetic_preference.id
        
        return render(self.request, 'polls/vote_success.html', {'poll_id': self.poll.id})

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.alternatives
        return kwargs

    def get_form_class(self) -> Type:
        num_judges = self.alternatives.count()
        return MajorityPreferenceFormSet.get_formset_class(num_judges)
        


class VoteShultzeView(View):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
