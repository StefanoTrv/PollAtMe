from django import forms
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from polls.forms import MajorityOpinionForm, MajorityPreferenceFormSet
from polls.models import Alternative, MajorityOpinionJudgement, Poll


class TestMajorityOpinionForm(TestCase):
    def setUp(self) -> None:
        self.poll = Poll(
            title="Lorem ipsum",
            text="Dolor sit amet",
            default_type=Poll.PollType.MAJORITY_JUDGMENT,
            start=timezone.now(),
            end=timezone.now() + timezone.timedelta(weeks=1),
            author=User.objects.create_user(username='test')
        )
        self.poll.save()
        self.poll.alternative_set.create(text="Lorem")
        self.poll.alternative_set.create(text="ipsum")
        self.poll.alternative_set.create(text="dolor")

    def test_empty(self):
        alternative: Alternative = self.poll.alternative_set.first()
        form = MajorityOpinionForm(alternative=alternative)
        self.assertIn('grade',form.fields)
        self.assertEqual(form.fields['grade'].label,alternative.text)
        self.assertIsInstance(form.fields['grade'].widget,forms.RadioSelect)

        for option in MajorityOpinionJudgement.JudgeType.choices:
            self.assertIn(option,form.fields['grade'].choices)
        
    
class TestMajorityPreferenceForm(TestCase):
    def setUp(self) -> None:
        self.poll = Poll(
            title="Lorem ipsum",
            text="Dolor sit amet",
            default_type=Poll.PollType.MAJORITY_JUDGMENT,
            start=timezone.now(),
            end=timezone.now() + timezone.timedelta(weeks=1),
            author=User.objects.create_user(username='test')
        )
        self.poll.save()
        self.poll.alternative_set.create(text="Lorem")
        self.poll.alternative_set.create(text="ipsum")
        self.poll.alternative_set.create(text="dolor")

    def test_empty(self):
        alternatives: Alternative = self.poll.alternative_set.all()
        formset_class = MajorityPreferenceFormSet.get_formset_class(alternatives.count())
        formset: MajorityPreferenceFormSet = formset_class(queryset = alternatives)
        
        self.assertEqual(len(formset.forms),alternatives.count())
