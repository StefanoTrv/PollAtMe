from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from polls import forms
from polls import models
from polls.services import create_poll_service

ALTERNATIVE_FORMSET = forms.BaseAlternativeFormSet.get_formset_class()


def select_action(request: HttpRequest, poll=None):
    action, queryset_alternatives = ('create', models.Poll.objects.none(
    )) if poll is None else ('edit', poll.alternative_set.all())

    if 'summary' in request.POST:
        return summary(request, action, queryset_alternatives, poll)

    if 'go_back' in request.POST:
        return go_back(request, action, queryset_alternatives, poll)

    if 'save' in request.POST:
        return save(request, action, queryset_alternatives, poll)


def summary(request: HttpRequest, action: str, alternatives: QuerySet, poll: Optional[models.Poll] = None):
    form_mainpoll = forms.PollFormMain(request.POST, instance=poll)
    formset_alternatives: forms.BaseAlternativeFormSet = ALTERNATIVE_FORMSET(request.POST, queryset=alternatives)

    if form_mainpoll.is_valid() and formset_alternatives.is_valid():
        form_poll: models.Poll = form_mainpoll.get_temporary_poll()
        
        if action not in request.session:
            request.session[action] = {}

        request.session[action].update({
            'page_1': formset_alternatives.get_form_for_session()
        })

        saved_data = request.session[action].get('page_2')
        saved_data.update(request.POST.dict()) if saved_data is not None else None
        request.session.modified = True
        
        return render(request, f'polls/create_poll/summary_and_options_{action}.html', {
            'alternatives': formset_alternatives.get_alternatives_text_list(),
            'form': forms.PollForm(saved_data, instance = form_poll),
            'mapping_form': forms.PollMappingForm(saved_data, instance = form_poll.mapping),
            'options_form': forms.PollOptionsForm(saved_data, instance = form_poll.polloptions),
        })
    else:
        formset_alternatives._non_form_errors[0] = "Inserisci almeno due alternative." #type: ignore
        for dict in formset_alternatives.errors:
            if 'This field is required.' in str(dict):
                dict['text'] = ''  # type: ignore

        return render(request, f'polls/create_poll/main_page_{action}.html', {
            'form': form_mainpoll,
            'formset': formset_alternatives,
        })


def go_back(request: HttpRequest, action: str, alternatives: QuerySet, poll: Optional[models.Poll] = None):

    request.session[action]['page_2'] = request.POST.dict()
    request.session.modified = True
    
    return render(request, f'polls/create_poll/main_page_{action}.html', {
        'form': forms.PollFormMain(request.POST, instance=poll),
        'formset': ALTERNATIVE_FORMSET(request.session[action]['page_1'], queryset=alternatives)
    })


def save(request: HttpRequest, action: str, alternatives: QuerySet, poll: Optional[models.Poll] = None):
    form_poll = forms.PollForm(request.POST, instance=poll)
    formset_alternatives: forms.BaseAlternativeFormSet = ALTERNATIVE_FORMSET(request.session[action]['page_1'], queryset=alternatives)
    form_mapping = forms.PollMappingForm(request.POST, instance=poll.mapping if poll is not None else None)
    form_options = forms.PollOptionsForm(request.POST, instance=poll.polloptions if poll is not None else None)

    if all((form_poll.is_valid(), formset_alternatives.is_valid(), form_mapping.is_valid(), form_options.is_valid())):
        saved_poll = create_poll_service(request.user, form_poll, form_mapping, form_options, formset_alternatives) # type: ignore
        if hasattr(saved_poll, models.Poll.AUTH_VOTE_TYPE_FIELDNAME):
            vote_type = 'authenticated'
        elif hasattr(saved_poll, models.Poll.TOKEN_VOTE_TYPE_FIELDNAME):
            vote_type = 'tokenized'
        else:
            vote_type = 'free'
        return render(request, f'polls/{action}_poll_success.html', {
            'id': saved_poll.id,
            'code': saved_poll.mapping.code,
            'title': saved_poll.title,
            'end': saved_poll.end,
            'vote_type': vote_type
        })
    else:
        return render(request, f'polls/create_poll/summary_and_options_{action}.html', {
            'form': form_poll,
            'alternatives': formset_alternatives.get_alternatives_text_list(),
            'mapping_form': form_mapping,
            'options_form': form_options,
        })


class CreatePollView(LoginRequiredMixin, TemplateView):

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, 'polls/create_poll/main_page_create.html', {
            'form': forms.PollFormMain(),
            'formset': forms.BaseAlternativeFormSet.get_formset_class()(queryset=models.Poll.objects.none())
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        return select_action(request)


class EditPollView(LoginRequiredMixin, TemplateView):

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.__poll: models.Poll = get_object_or_404(models.Poll, id=kwargs['id'])

        if self.__poll.is_active():
            raise PermissionDenied(
                "Non è possibile modificare il sondaggio perché è in corso la votazione")

        if self.__poll.is_ended():
            raise PermissionDenied(
                "Questo sondaggio è concluso e non può essere modificato")

        if not self.__poll.author.__eq__(request.user):
            raise PermissionDenied(
                "Non hai i permessi per modificare questo sondaggio")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, 'polls/create_poll/main_page_edit.html', {
            'form': forms.PollFormMain(instance=self.__poll),
            'formset': forms.BaseAlternativeFormSet.get_formset_class()(queryset=self.__poll.alternative_set.all())
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        return select_action(request, self.__poll)
