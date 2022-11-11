from typing import *

from django import forms
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.core.exceptions import ObjectDoesNotExist

from polls.models import Vote, Choice, Question


class VoteView(CreateView):
    model: type[models.Model] = Vote
    fields: list[str] = ['choice']
    template_name: str = 'vote_create_form.html'

    question: Question = Question()

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.__getQuestion(question_id=kwargs['id'])
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.__getQuestion(question_id=kwargs['id'])
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['question'] = self.question
        return context

    def get_form(self, form_class: Type[forms.BaseModelForm] = None):
        form = super().get_form(form_class)
        form.fields['choice'] = forms.ModelChoiceField(
            queryset=Choice.objects.filter(question=self.question),
            widget=forms.RadioSelect
        )
        return form

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        form.instance.question = self.question
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('polls:vote', kwargs={'id': self.question.id})

    def __getQuestion(self, question_id):
        try:
            self.question = Question.objects.get(id=question_id)
            if  self.question.choice_set.count() == 0:
                self.question = None
        except ObjectDoesNotExist:
            self.question = None