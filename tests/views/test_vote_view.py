from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls import forms as pollforms
from polls import models

URL = 'polls:vote'

class TestCreateSinglePreferenceView(TestCase):
    fixtures = ['polls.json']
    
    def setUp(self) -> None:
        self.poll = models.Poll.objects.first()
        if self.poll is not None:
            self.url = reverse(URL, args=[self.poll.pk])
            self.form = pollforms.SinglePreferenceForm(poll=self.poll)

    def test_show_single_preference_poll_form(self):
        res = self.client.get(self.url)
        self.assertIsInstance(res.context['form'], pollforms.SinglePreferenceForm)
        
        self.assertContains(
            response=res,
            text=self.poll.text
        )
        for alternative in models.Alternative.objects.filter(poll = self.poll.id):
            self.assertContains(res, alternative.text)

    def test_submit_and_save_in_db(self):
        last_vote_old = models.SinglePreference.objects.last()
        alternative_count_old = len(models.SinglePreference.objects.filter(alternative = 1))
        resp = self.client.post(self.url, data = {
            'alternative' : 1,
        })
        self.assertEqual(resp.status_code,200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )

        last_vote = models.SinglePreference.objects.last()
        self.assertNotEqual(last_vote.id,last_vote_old.id)

        self.assertEqual(len(models.SinglePreference.objects.filter(alternative = 1)),alternative_count_old+1)
            
    def test_404_sondaggio_inesistente(self):
        url = reverse(URL, args=[100])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)      

    def test_sondaggio_senza_scelte(self):
        empty_poll = models.Poll()
        empty_poll.title = 'Title'
        empty_poll.text = 'Text'
        empty_poll.start = timezone.now()
        empty_poll.end = timezone.now()
        empty_poll.author = User.objects.get(username='test')
        empty_poll.save()
        url = reverse(URL, args=[empty_poll.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_if_submit_and_save_in_db(self):
        last_vote_old = models.SinglePreference.objects.last()
        resp = self.client.post(self.url, {
            'alternative': 2
        })

        self.assertEqual(resp.status_code,200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )
        last_vote = models.SinglePreference.objects.last()
        self.assertNotEqual(last_vote.id,last_vote_old.id)
        self.assertEqual(last_vote.alternative.id,2)


class TestCreateMajorityPreferenceView(TestCase):
    fixtures = ['polls.json']

    def setUp(self) -> None:
        self.poll = models.Poll.objects.filter(default_type=models.Poll.PollType.MAJORITY_JUDGMENT).first()
        if self.poll is not None:
            self.url = reverse(URL, args=[self.poll.pk])
            self.resp = self.client.get(self.url)
            self.formset_class = pollforms.MajorityPreferenceFormSet.get_formset_class(
                self.poll.alternative_set.count())
            self.form = self.formset_class(queryset=self.poll.alternative_set.all())
        return super().setUp()

    def test_show_majority_preference_poll_form(self):
        self.assertEqual(len(self.resp.context['form'].forms),len(self.form.forms))
        self.assertEqual(self.resp.status_code,200)
        self.assertContains(
            response=self.resp,
            text=str(self.form.management_form)
        )
        self.assertContains(
            response=self.resp,
            text=self.poll.title
        )
        self.assertContains(
            response=self.resp,
            text=self.poll.text
        )

        f: pollforms.MajorityOpinionForm
        for f in self.form:
            self.assertContains(
                response=self.resp,
                text=f.fields['grade'].label
            )
    
    def test_submit_and_save_in_db(self):
        last_vote_old = models.MajorityPreference.objects.last()
        resp = self.client.post(self.url, {
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
        self.assertEqual(resp.status_code,200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )

        last_vote = models.MajorityPreference.objects.last()
        self.assertNotEqual(last_vote.id,last_vote_old.id)

        judge: models.MajorityOpinionJudgement
        for judge in last_vote.majorityopinionjudgement_set.all():
            self.assertEqual(judge.grade,1)
