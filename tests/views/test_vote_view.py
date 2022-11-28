from django.test import Client, TestCase
from polls.models import SinglePreferencePoll, MajorityOpinionPoll
from django.urls import reverse
from assertpy import assert_that  # type: ignore
from polls import forms as pollforms
from django import forms


class TestCreateSinglePreferenceView(TestCase):
    fixtures = ['polls.json']
    client = Client()

    def test_if_show_single_preference_poll_form(self):
        poll = SinglePreferencePoll.objects.first()
        url = reverse('polls:vote', args=[poll.pk])
        res = self.client.get(url)
        form = pollforms.SinglePreferenceForm(poll=poll)
        assert_that(res.context['form']).is_instance_of(pollforms.SinglePreferenceForm)
        self.assertContains(
            response=res,
            text=str(form),
            status_code=200
        )

class TestCreateMajorityPreferenceView(TestCase):
    fixtures = ['polls.json']
    client = Client()

    def test_if_show_majority_preference_poll_form(self):
        poll = MajorityOpinionPoll.objects.first()
        url = reverse('polls:vote', args=[poll.pk])
        res = self.client.get(url)
        formset_class = pollforms.MajorityPreferenceFormSet.get_formset_class(
            poll.alternative_set.count())
        form = formset_class(queryset=poll.alternative_set.all())
        assert_that(res.context['form'].forms).is_length(len(form.forms))
        assert_that(res.status_code).is_equal_to(200)
        self.assertContains(
            response=res,
            text=str(form.management_form)
        )
        f: pollforms.MajorityOpinionForm
        for f in form:
            self.assertContains(
                response=res,
                text=f.fields['grade'].label
            )
