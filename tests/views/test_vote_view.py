from assertpy import assert_that  # type: ignore
from django.test import Client, TestCase
from django.urls import reverse

from polls import forms as pollforms
from polls import models

URL = 'polls:vote'

class TestCreateSinglePreferenceView(TestCase):
    fixtures = ['polls.json']
    client = Client()

    def setUp(self) -> None:
        self.poll = models.SinglePreferencePoll.objects.first()
        if self.poll is not None:
            self.url = reverse(URL, args=[self.poll.pk])
            self.form = pollforms.SinglePreferenceForm(poll=self.poll)
        return super().setUp()

    def test_if_show_single_preference_poll_form(self):
        res = self.client.get(self.url)
        assert_that(res.context['form']).is_instance_of(pollforms.SinglePreferenceForm)
        
        #self.assertContains(
        #    response=res,
        #    text=self.poll.title
        #)
        self.assertContains(
            response=res,
            text=self.poll.text
        )
        for alternative in models.Alternative.objects.filter(poll = self.poll.id):
            self.assertContains(res, alternative.text)
    
    def test_404_sondaggio_inesistente(self):
        url = reverse(URL, args=[100])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Il sondaggio ricercato non esiste')        

    def test_sondaggio_senza_scelte(self):
        empty_poll = models.SinglePreferencePoll()
        empty_poll.title = 'Title'
        empty_poll.text = 'Text'
        empty_poll.save()
        url = reverse(URL, args=[empty_poll.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Il sondaggio ricercato non ha opzioni di risposta')    

    def test_if_submit_and_save_in_db(self):
        last_vote_before = models.SinglePreference.objects.last()
        res = self.client.post(self.url, {
            'alternative': 2
        })

        assert_that(res.status_code).is_equal_to(200)
        self.assertTemplateUsed(
            response=res,
            template_name='vote_success.html'
        )
        last_vote = models.SinglePreference.objects.last()
        assert_that(last_vote.id).is_not_equal_to(last_vote_before.id)
        assert_that(last_vote.alternative.id).is_equal_to(2)


class TestCreateMajorityPreferenceView(TestCase):
    fixtures = ['polls.json']
    client = Client()

    def setUp(self) -> None:
        self.poll = models.MajorityOpinionPoll.objects.first()
        if self.poll is not None:
            self.url = reverse(URL, args=[self.poll.pk])
            self.res = self.client.get(self.url)
            self.formset_class = pollforms.MajorityPreferenceFormSet.get_formset_class(
                self.poll.alternative_set.count())
            self.form = self.formset_class(queryset=self.poll.alternative_set.all())
        return super().setUp()

    def test_if_show_majority_preference_poll_form(self):
        assert_that(self.res.context['form'].forms).is_length(len(self.form.forms))
        assert_that(self.res.status_code).is_equal_to(200)
        self.assertContains(
            response=self.res,
            text=str(self.form.management_form)
        )
        self.assertContains(
            response=self.res,
            text=self.poll.title
        )
        self.assertContains(
            response=self.res,
            text=self.poll.text
        )

        f: pollforms.MajorityOpinionForm
        for f in self.form:
            self.assertContains(
                response=self.res,
                text=f.fields['grade'].label
            )
    
    def test_if_submit_and_save_in_db(self):
        last_vote_before = models.MajorityPreference.objects.last()
        res = self.client.post(self.url, {
            'majorityopinionjudgement_set-TOTAL_FORMS': 5,
            'majorityopinionjudgement_set-INITIAL_FORMS': 0,
            'majorityopinionjudgement_set-MIN_NUM_FORMS': 5,
            'majorityopinionjudgement_set-MAX_NUM_FORMS': 5,
            'majorityopinionjudgement_set-0-grade': 1,
            'majorityopinionjudgement_set-1-grade': 1,
            'majorityopinionjudgement_set-2-grade': 1,
            'majorityopinionjudgement_set-3-grade': 1,
            'majorityopinionjudgement_set-4-grade': 1,
        })
        assert_that(res.status_code).is_equal_to(200)
        self.assertTemplateUsed(
            response=res,
            template_name='vote_success.html'
        )

        last_vote = models.MajorityPreference.objects.last()
        assert_that(last_vote.id).is_not_equal_to(last_vote_before.id)

        judge: models.MajorityOpinionJudgement
        for judge in last_vote.responses.through.all():
            assert_that(judge.grade).is_equal_to(1)
