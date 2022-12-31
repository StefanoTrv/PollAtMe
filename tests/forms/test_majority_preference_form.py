from django.test import TestCase
from polls.forms import MajorityOpinionForm, MajorityPreferenceFormSet
from polls.models import MajorityOpinionPoll, MajorityOpinionJudgement, Alternative
from django import forms
from django.db.models import QuerySet

class TestMajorityOpinionForm(TestCase):
    fixtures = ['polls.json']

    def test_empty(self):
        poll = MajorityOpinionPoll.objects.all()[0]
        alternative: Alternative = poll.alternative_set.all()[0]
        form = MajorityOpinionForm(alternative=alternative)
        self.assertIn('grade',form.fields)
        self.assertEqual(form.fields['grade'].label,alternative.text)
        self.assertIsInstance(form.fields['grade'].widget,forms.RadioSelect)

        for option in MajorityOpinionJudgement.JudgeType.choices:
            self.assertIn(option,form.fields['grade'].choices)
        
    
class TestMajorityPreferenceForm(TestCase):
    fixtures = ['polls.json']

    def test_empty(self):
        poll = MajorityOpinionPoll.objects.all()[0]
        alternatives: QuerySet[Alternative] = poll.alternative_set.all()
        formset_class = MajorityPreferenceFormSet.get_formset_class(alternatives.count())
        formset: MajorityPreferenceFormSet = formset_class(queryset = alternatives)
        
        self.assertEqual(len(formset.forms),alternatives.count())
