from django.test import TestCase
from polls.forms import SinglePreferenceForm
from polls.models import Poll, SinglePreference, Alternative
from django import forms
from django.utils import timezone


class TestSinglePreferenceForm(TestCase):

    def setUp(self) -> None:
        poll = Poll(
            title="Lorem ipsum",
            text="Dolor sit amet",
            default_type=Poll.PollType.SINGLE_PREFERENCE,
            start=timezone.now(),
            end=timezone.now() + timezone.timedelta(weeks=1)
        )
        poll.save()
        poll.alternative_set.create(text="Lorem")
        poll.alternative_set.create(text="ipsum")

    def test_empty_form(self):
        poll = Poll.objects.last()
        form = SinglePreferenceForm(poll=poll)
        self.assertIn('alternative', form.fields)
        self.assertIsInstance(
            form.fields['alternative'].widget, forms.RadioSelect)
        self.assertEqual(
            len(form.fields['alternative'].choices), poll.alternative_set.count())

        for alternative in poll.alternative_set.all():
            self.assertIn(
                alternative, form.fields['alternative'].choices.queryset)

    def test_insertion(self):
        poll = Poll.objects.last()
        alt = Alternative.objects.get(text="Lorem")
        form = SinglePreferenceForm({'alternative': alt.id}, poll=poll)
        instance: SinglePreference = form.save(commit=False)
        instance.poll = poll
        instance.save()

        self.assertIsNotNone(instance.pk)
        self.assertEqual(instance.alternative.id, alt.id)
