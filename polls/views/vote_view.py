from typing import Any, Optional, Type

from django import forms, http
from django.contrib.auth.views import redirect_to_login
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.edit import CreateView

from polls.exceptions import PollWithoutAlternativesException
from polls import forms as pf
from polls.models import Poll
from polls.models import preference as pref
from polls.services import SearchPollService, check


# se si accede alla pagina di voto generica, si viene reindirizzati alla pagina di voto del metodo principale
def vote_redirect_view(request, id, token=None):
    poll = SearchPollService().search_by_id(id)
    if token is None:
        args = [id]
    else:
        args = [id, token]

    if poll.default_type == Poll.PollType.SINGLE_PREFERENCE:
        return redirect(reverse('polls:vote_single_preference', args=args))

    if poll.default_type == Poll.PollType.MAJORITY_JUDGMENT:
        return redirect(reverse('polls:vote_MJ', args=args))
    
    if poll.default_type == Poll.PollType.SHULTZE_METHOD:
        return redirect(reverse('polls:vote_shultze', args=args))


class _VoteView(CreateView):
    """
    Class view (de facto astratta) che incorpora ciò che hanno in comune le diverse pagine di voto
    """
    poll: Poll
    pollType: str
    alternatives: QuerySet

    def dispatch(self, request, *args, **kwargs):
        try:
            self.poll = SearchPollService().search_by_id(kwargs['id'])
        except PollWithoutAlternativesException:
            raise http.Http404(
                "Il sondaggio ricercato non ha opzioni di risposta")
        syntethic_preference = self.__get_syntethic_preference(
            request.session.get('preference_id', None))
        self.alternatives = self.poll.alternative_set.all()
        self.token = kwargs.get('token', '').replace('-', ' ')

        check_passed = self.__get_authorization_checker(
            request, 
            syntethic_preference).handle()

        return check_passed if check_passed else super().dispatch(request, *args, **kwargs)

    def __get_syntethic_preference(self, id):
        if id is None or self.poll.get_type() == self.pollType:
            return None

        if self.pollType == "Preferenza singola":
            vote_class = pref.SinglePreference

        if self.pollType == "Giudizio maggioritario":
            vote_class = pref.MajorityPreference

        return vote_class.objects.get(id=id)

    def __failed_authentication(self):
        if self.poll.authentication_type == Poll.PollAuthenticationType.AUTHENTICATED:
            self.request.session['auth_message'] = 'Devi aver effettuato il login per poter votare questa scelta'
            return redirect_to_login(self.request.get_full_path())

        if self.poll.authentication_type == Poll.PollAuthenticationType.TOKENIZED:
            return render(self.request, 'polls/token_request.html', {'poll': self.poll, 'token': self.token})

    def __get_authorization_checker(self, request: http.HttpRequest, syntethic_preference):
        handler = check.CheckPollActiveness(self.poll)
        handler \
            .set_next(check.CheckAuthentication(
                self.poll, 
                request.user.is_authenticated, 
                self.token, 
                self.__failed_authentication)) \
            .set_next(check.CheckUserHasVoted(
                self.poll, 
                request.user, 
                self.token, 
                syntethic_preference,
                lambda: render(self.request, 'polls/already_voted.html', {'poll': self.poll}))) \
            .set_next(check.CheckRevoteSession(
                self.poll, 
                self.pollType, 
                'preference_id' in request.session, 
                syntethic_preference))
        return handler

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        return context


class VoteSinglePreferenceView(_VoteView):

    form_class: Optional[Type[forms.BaseForm]] = pf.SinglePreferenceForm
    template_name: str = 'polls/vote/vote_SP.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.pollType = Poll.PollType.SINGLE_PREFERENCE.label

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Inizializzo gli argomenti per il form, in questo caso la poll
        da cui estrarre le opzioni
        """
        kwargs = super().get_form_kwargs()
        kwargs['poll'] = self.poll
        return kwargs

    def form_valid(self, form: forms.BaseModelForm) -> http.HttpResponse:
        self.poll.set_authentication_method_as_used(
            user=self.request.user, token=self.token)

        form.instance.poll = self.poll
        new_preference = form.save()

        if self.poll.get_type() == self.pollType:
            synthetic_preference = pref.MajorityPreference.save_mj_from_sp(
                new_preference)
            self.request.session['preference_id'] = synthetic_preference.id
            self.request.session['alternative_sp'] = new_preference.alternative.text
            return render(self.request, 'polls/vote_success.html', {'poll': self.poll, 'revote': True, 'token': self.token})

        return render(self.request, 'polls/vote_success.html', {'poll': self.poll})


class VoteMajorityJudgmentView(_VoteView):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
    template_name: str = 'polls/vote/vote_GM.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.pollType = Poll.PollType.MAJORITY_JUDGMENT.label

    def form_valid(self, form: forms.BaseInlineFormSet) -> http.HttpResponse:
        synthetic_id = self.request.session.pop('preference_id', False)
        if not synthetic_id:
            self.poll.set_authentication_method_as_used(
                user=self.request.user, token=self.token)

        if synthetic_id:
            preference = pref.MajorityPreference.objects.get(id=synthetic_id)
        else:
            preference = pref.MajorityPreference()
            preference.poll = self.poll

        preference.synthetic = False
        preference.save()
        preference.save_mj_judgements(form.save(commit=False))

        return render(self.request, 'polls/vote_success.html', {'poll': self.poll})

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.alternatives
        return kwargs

    def get_form_class(self) -> Type:
        num_judges = self.alternatives.count()
        return pf.MajorityPreferenceFormSet.get_formset_class(num_judges)


class VoteShultzeView(_VoteView):
    """
    Class view per l'inserimento delle risposte ai sondaggi con metodo Shultze
    """
    template_name: str = 'polls/vote/vote_SHULTZE.html'


    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.pollType = Poll.PollType.SHULTZE_METHOD.label
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.poll.set_authentication_method_as_used(
            user=self.request.user, token=self.token)
    
        preference = pref.ShultzePreference()
        preference.poll = self.poll
        preference.save()
        preference.save_shulze_judgements(form.save(commit=False))

        if self.poll.get_type() == self.pollType:
            syntethic_preference = pref.MajorityPreference.save_mj_from_shultze(preference)
            self.request.session['preference_id'] = syntethic_preference.id
            self.request.session['sequence_shultze'] = [alt.alternative.text for alt in preference.shultzeopinionjudgement_set.order_by('order').all()]
            return render(self.request, 'polls/vote_success.html', {'poll': self.poll, 'revote': True, 'token': self.token})

        return render(self.request, 'polls/vote_success.html', {'poll': self.poll})

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.alternatives
        return kwargs
    
    def get_form_class(self) -> Type[BaseModelForm]:
        num_judges = self.alternatives.count()
        return pf.ShultzePreferenceFormSet.get_formset_class(num_judges)