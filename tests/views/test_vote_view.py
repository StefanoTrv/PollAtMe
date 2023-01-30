from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls import forms as pollforms
from polls import models

from assertpy import assert_that  # type: ignore

    
class TestCreateSinglePreferenceView(TestCase):
    fixtures = ['polls.json']
    URL = 'polls:vote_single_preference'
    
    def setUp(self) -> None:
        self.poll = models.Poll.objects.first()
        if self.poll is not None:
            self.poll_url = reverse('polls:vote_single_preference', args=[self.poll.pk])
            self.form = pollforms.SinglePreferenceForm(poll=self.poll)

    def test_show_single_preference_poll_form(self):
        res = self.client.get(self.poll_url)
        self.assertIsInstance(res.context['form'], pollforms.SinglePreferenceForm)
        
        self.assertContains(
            response=res,
            text=self.poll.text
        )
        for alternative in models.Alternative.objects.filter(poll = self.poll.id):
            self.assertContains(res, alternative.text)

    def test_submit_and_save_in_db(self):
        last_vote_old = models.SinglePreference.objects.last()
        preference_count_old = len(models.SinglePreference.objects.filter(alternative = 1))
        resp = self.client.post(self.poll_url, data = {
            'alternative' : 1,
        })
        self.assertEqual(resp.status_code,200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )

        last_vote = models.SinglePreference.objects.last()
        self.assertNotEqual(last_vote.id,last_vote_old.id)

        self.assertEqual(len(models.SinglePreference.objects.filter(alternative = 1)),preference_count_old+1)
            
    def test_404_sondaggio_inesistente(self):
        url = reverse(self.URL, args=[100])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code,404)

    def test_sondaggio_senza_scelte(self):
        empty_poll = models.Poll()
        empty_poll.title = 'Title'
        empty_poll.text = 'Text'
        empty_poll.start = timezone.now()
        empty_poll.end = timezone.now()
        empty_poll.author = User.objects.get(username='test')
        empty_poll.save()
        url = reverse(self.URL, args=[empty_poll.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_if_submit_and_save_in_db(self):
        last_vote_old = models.SinglePreference.objects.last()
        resp = self.client.post(self.poll_url, {
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
    
    def test_creates_synthetic_MJ_vote(self):
        last_preference_old = models.MajorityPreference.objects.last()
        preference_count_old = len(models.MajorityPreference.objects.all())
        self.client.post(self.poll_url, data = {
            'alternative' : 1,
        })

        last_preference = models.MajorityPreference.objects.last()
        self.assertNotEqual(last_preference.id,last_preference_old.id)
        assert_that(last_preference.synthetic).is_equal_to(True)
        self.assertEqual(len(models.MajorityPreference.objects.all()),preference_count_old+1)

        for opinion in last_preference.majorityopinionjudgement_set.all():
            if opinion.alternative.id==1:
                assert_that(opinion.grade).is_equal_to(5)
            else:
                assert_that(opinion.grade).is_equal_to(1)
        
    def test_revote(self):
        self.client.post(self.poll_url, data = {
            'alternative' : 1,
        })

        synthetic_vote_id = models.MajorityPreference.objects.last().id
        revote_url=reverse('polls:vote_MJ', args=[self.poll.pk])
        resp = self.client.get(revote_url)
        self.assertEqual(resp.status_code,200)
        resp = self.client.post(revote_url, {
            'majorityopinionjudgement_set-TOTAL_FORMS': 4,
            'majorityopinionjudgement_set-INITIAL_FORMS': 0,
            'majorityopinionjudgement_set-MIN_NUM_FORMS': 4,
            'majorityopinionjudgement_set-MAX_NUM_FORMS': 4,
            'majorityopinionjudgement_set-0-grade': 1,
            'majorityopinionjudgement_set-1-grade': 1,
            'majorityopinionjudgement_set-2-grade': 1,
            'majorityopinionjudgement_set-3-grade': 1,
        })
        self.assertEqual(resp.status_code,200)
        assert_that(models.MajorityPreference.objects.filter(id=synthetic_vote_id)).is_empty()
        assert_that(models.MajorityPreference.objects.last().poll).is_equal_to(self.poll)
        for judgement in models.MajorityPreference.objects.last().majorityopinionjudgement_set.all():
            self.assertEqual(judgement.grade,1)


class TestCreateMajorityPreferenceView(TestCase):
    fixtures = ['polls.json']
    URL = 'polls:vote_MJ'

    def setUp(self) -> None:
        self.poll = models.Poll.objects.filter(default_type=models.Poll.PollType.MAJORITY_JUDGMENT).first()
        if self.poll is not None:
            self.poll_url = reverse(self.URL, args=[self.poll.pk])
            self.resp = self.client.get(self.poll_url)
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
        resp = self.client.post(self.poll_url, {
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

        judgement: models.MajorityOpinionJudgement
        for judgement in last_vote.majorityopinionjudgement_set.all():
            self.assertEqual(judgement.grade,1)
    
    def test_creates_synthetic_single_preference_vote(self):
        last_preference_old = models.SinglePreference.objects.last()
        preference_count_old = len(models.SinglePreference.objects.all())
        self.client.post(self.poll_url, {
            'majorityopinionjudgement_set-TOTAL_FORMS': 5,
            'majorityopinionjudgement_set-INITIAL_FORMS': 0,
            'majorityopinionjudgement_set-MIN_NUM_FORMS': 5,
            'majorityopinionjudgement_set-MAX_NUM_FORMS': 5,
            'majorityopinionjudgement_set-0-grade': 5,
            'majorityopinionjudgement_set-1-grade': 1,
            'majorityopinionjudgement_set-2-grade': 1,
            'majorityopinionjudgement_set-3-grade': 1,
            'majorityopinionjudgement_set-4-grade': 1,
        })

        last_preference = models.SinglePreference.objects.last()
        self.assertNotEqual(last_preference.id,last_preference_old.id)
        assert_that(last_preference.synthetic).is_equal_to(True)
        self.assertEqual(len(models.SinglePreference.objects.all()),preference_count_old+1)
        assert_that(last_preference.alternative.id).is_equal_to(5)
        
    def test_revote(self):
        self.client.post(self.poll_url, {
            'majorityopinionjudgement_set-TOTAL_FORMS': 5,
            'majorityopinionjudgement_set-INITIAL_FORMS': 0,
            'majorityopinionjudgement_set-MIN_NUM_FORMS': 5,
            'majorityopinionjudgement_set-MAX_NUM_FORMS': 5,
            'majorityopinionjudgement_set-0-grade': 1,
            'majorityopinionjudgement_set-1-grade': 1,
            'majorityopinionjudgement_set-2-grade': 5,
            'majorityopinionjudgement_set-3-grade': 1,
            'majorityopinionjudgement_set-4-grade': 1,
        })

        synthetic_vote_id = models.SinglePreference.objects.last().id
        revote_url=reverse('polls:vote_single_preference', args=[self.poll.pk])
        resp = self.client.get(revote_url)
        self.assertEqual(resp.status_code,200)
        resp = self.client.post(revote_url, {
            'alternative' : 5,
        })
        self.assertEqual(resp.status_code,200)
        assert_that(models.SinglePreference.objects.filter(id=synthetic_vote_id)).is_empty()
        assert_that(models.SinglePreference.objects.last().poll).is_equal_to(self.poll)
        assert_that(models.SinglePreference.objects.last().alternative).is_equal_to(self.poll.alternative_set.first())
