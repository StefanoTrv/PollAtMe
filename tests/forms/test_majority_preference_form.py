from django.test import TestCase
from polls.forms import MajorityOpinionForm, MajorityPreferenceFormSet
from polls.models import MajorityOpinionPoll, MajorityOpinionJudgement, MajorityPreference, Alternative
from assertpy import assert_that #type:ignore
from django import forms
from django.db.models import QuerySet

class TestMajorityOpinionForm(TestCase):
    fixtures = ['polls.json']

    def test_empty(self):
        poll = MajorityOpinionPoll.objects.all()[0]
        alternative: Alternative = poll.alternative_set.all()[0]
        form = MajorityOpinionForm(alternative=alternative)
        assert_that(form.fields).contains('grade')
        assert_that(form.fields['grade'].label).is_equal_to(alternative.text)
        assert_that(form.fields['grade'].widget).is_instance_of(forms.RadioSelect)

        for option in MajorityOpinionJudgement.JudgeType.choices:
            assert_that(form.fields['grade'].choices).contains(option)
        
    
class TestMajorityPreferenceForm(TestCase):
    fixtures = ['polls.json']

    def test_empty(self):
        poll = MajorityOpinionPoll.objects.all()[0]
        alternatives: QuerySet[Alternative] = poll.alternative_set.all()
        formset_class = MajorityPreferenceFormSet.get_formset_class(alternatives.count())
        formset: MajorityPreferenceFormSet = formset_class(queryset = alternatives)
        
        assert_that(formset.forms).is_length(alternatives.count())
