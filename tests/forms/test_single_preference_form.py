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
        self.assertIn('alternative',form.fields)
        self.assertIsInstance(form.fields['alternative'].widget,forms.RadioSelect)
        self.assertEqual(len(form.fields['alternative'].choices),poll.alternative_set.count())
        
        for alternative in poll.alternative_set.all():
            self.assertIn(alternative,form.fields['alternative'].choices.queryset)
    
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
        
        self.assertIsNotNone(instance.pk)
        self.assertEqual(instance.alternative.id,2)
    
