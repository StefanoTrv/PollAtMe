from typing import Optional

from django.http import HttpRequest
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.utils import timezone
from datetime import timedelta

from polls.models import Poll
from polls.forms import PollFormAdditionalOptions, PollFormMain, BaseAlternativeFormSet, PollMappingForm

from django.contrib.auth.mixins import LoginRequiredMixin

from polls.models.mapping import Mapping


ALTERNATIVE_FORMSET = BaseAlternativeFormSet.get_formset_class()


def select_action(request: HttpRequest, poll=None):
    action, queryset_alternatives = ('create', Poll.objects.none(
    )) if poll is None else ('edit', poll.alternative_set.all())

    if 'summary' in request.POST:
        return summary(request, action, queryset_alternatives, poll)

    if 'go_back' in request.POST:
        return go_back(request, action, queryset_alternatives, poll)

    if 'save' in request.POST:
        return save(request, action, queryset_alternatives, poll)


def summary(request: HttpRequest, action: str, alternatives: QuerySet, poll: Optional[Poll] = None):
    form = PollFormMain(request.POST, instance=poll)
    formset_alternatives: BaseAlternativeFormSet = ALTERNATIVE_FORMSET(
        request.POST, queryset=alternatives)

    if form.is_valid() and formset_alternatives.is_valid():
        f_poll: Poll = form.save(commit=False)
        if f_poll.start is None:
            f_poll.start = timezone.now() + timedelta(minutes=10)
            f_poll.end = f_poll.start + timedelta(weeks=2)
        if f_poll.author_id is None:
            f_poll.author = request.user
        request.session[action] = {
            'poll': form.cleaned_data,
            'alternatives': formset_alternatives.get_form_for_session()
        }

        existing_mapping = None
        if poll != None:
            if Mapping.objects.filter(poll=poll).count() > 0:
                existing_mapping = Mapping.objects.filter(poll=poll).get()

        return render(request, f'polls/create_poll/summary_and_options_{action}.html', {
            'alternatives': formset_alternatives.get_alternatives_text_list(),
            'form': PollFormAdditionalOptions(instance=f_poll),
            'mapping_form': PollMappingForm(instance=existing_mapping)
        })
    else:
        formset_alternatives._non_form_errors[0]=str(formset_alternatives._non_form_errors[0]).replace("Please submit at least 2 forms.","Inserisci almeno due alternative.") # type: ignore
        print(formset_alternatives.errors)
        for dict in formset_alternatives.errors:
            if 'This field is required.' in str(dict):
                dict['text']='' # type: ignore
        return render(request, f'polls/create_poll/main_page_{action}.html', {
            'form': form,
            'formset': formset_alternatives,
        })


def go_back(request: HttpRequest, action: str, alternatives: QuerySet, poll: Optional[Poll] = None):
    return render(request, f'polls/create_poll/main_page_{action}.html', {
        'form': PollFormMain(request.session[action]['poll'], instance=poll),
        'formset': ALTERNATIVE_FORMSET(request.session[action]['alternatives'], queryset=alternatives)
    })


def save(request: HttpRequest, action: str, alternatives: QuerySet, poll: Optional[Poll] = None):
    form = PollFormAdditionalOptions(request.POST, instance=poll)
    formset_alternatives: BaseAlternativeFormSet = ALTERNATIVE_FORMSET(
        request.session[action]['alternatives'], queryset=alternatives)
    
    if poll is None:
        mapping = None
    else:
        mapping = poll.mapping_set.first()

    form_mapping: PollMappingForm = PollMappingForm(request.POST, instance=mapping)

    if form.is_valid() and formset_alternatives.is_valid() and form_mapping.is_valid():
        saved_poll = form.save()

        saved_mapping = form_mapping.save(commit=False)
        saved_mapping.poll = saved_poll
        saved_mapping.save()

        formset_alternatives.save(commit=False)
        for alt in formset_alternatives.new_objects:
            alt.poll = saved_poll
            alt.save()

        for alt in formset_alternatives.changed_objects:
            alt[0].save()

        for alt in formset_alternatives.deleted_objects:
            alt.delete()

        return render(request, f'polls/{action}_poll_success.html', {
            'code' : saved_mapping.code
        })
    else:
        return render(request, f'polls/create_poll/summary_and_options_{action}.html', {
            'form': form,
            'alternatives': formset_alternatives.get_alternatives_text_list(),
            'mapping_form': form_mapping
        })


class CreatePollView(LoginRequiredMixin, TemplateView):

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, 'polls/create_poll/main_page_create.html', {
            'form': PollFormMain(),
            'formset': BaseAlternativeFormSet.get_formset_class()(queryset=Poll.objects.none())
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        return select_action(request)


class EditPollView(LoginRequiredMixin, TemplateView):

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.__poll: Poll = get_object_or_404(Poll, id=kwargs['id'])

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
            'form': PollFormMain(instance=self.__poll),
            'formset': BaseAlternativeFormSet.get_formset_class()(queryset=self.__poll.alternative_set.all())
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        return select_action(request, self.__poll)
