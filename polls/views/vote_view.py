from typing import *

from django import forms
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic.edit import CreateView

from polls.models import Answer, Choice, Question


class AnswerView(CreateView):
    model: type[models.Model] = Answer
    fields: list[str] = ['choice']
    template_name_suffix: str = '_create_form'

    question: Question = Question()

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.question = Question.objects.get(id=kwargs['id'])
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.question = Question.objects.get(id=kwargs['id'])
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_text'] = self.question.question_text
        return context
    
    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields['choice'] = forms.ModelChoiceField(
            queryset=Choice.objects.all(),
            widget=forms.RadioSelect
            )
        return form

    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        form.instance.question = self.question
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('polls:vote', kwargs={'id': self.question.id})
    