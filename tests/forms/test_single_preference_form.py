from django.test import TestCase
from polls.forms import SinglePreferenceForm
from polls.models import Poll, SinglePreference
from django.http import HttpRequest
from assertpy import assert_that #type: ignore
from django import forms

class TestSinglePreferenceForm(TestCase):

    fixtures = ['polls.json']

    def test_empty_form(self):
        poll = Poll.objects.get(pk=1)
        form = SinglePreferenceForm(poll=poll)
        assert_that(form.fields).contains('alternative')
        assert_that(form.fields['alternative'].widget).is_instance_of(forms.RadioSelect)
        assert_that(form.fields['alternative'].choices).is_length(poll.alternative_set.count())
        
        for alternative in poll.alternative_set.all():
            assert_that(form.fields['alternative'].choices.queryset).contains(alternative)
    
    def test_insertion(self):
        request = HttpRequest()
        poll = Poll.objects.get(pk=1)

        request.POST = {
            'alternative': 2
        }

        form = SinglePreferenceForm(request.POST, poll=poll)
        instance: SinglePreference = form.save(commit=False)
        instance.poll = poll
        instance.save()
        
        assert_that(instance.pk).is_not_none()
        assert_that(instance.alternative.id).is_equal_to(2)
    
