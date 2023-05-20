import re

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls import forms as pollforms
from polls import models

from assertpy import assert_that  # type: ignore


def remove_csfr_token(response):
    return re.sub(
        r"<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\".{64}\">",
        '',
        response.content.decode()
    )


class TestVoteSinglePreferenceView(TestCase):
    fixtures = ['polls.json']
    URL = 'polls:vote_single_preference'

    def setUp(self) -> None:
        self.poll = models.Poll.objects.first()
        if self.poll is not None:
            self.poll_url = reverse(
                'polls:vote_single_preference', args=[self.poll.pk])
            self.form = pollforms.SinglePreferenceForm(poll=self.poll)

    def test_show_single_preference_poll_form(self):
        res = self.client.get(self.poll_url)
        self.assertIsInstance(
            res.context['form'], pollforms.SinglePreferenceForm)

        self.assertContains(
            response=res,
            text=self.poll.text
        )
        for alternative in models.Alternative.objects.filter(poll=self.poll.id):
            self.assertContains(res, alternative.text)

    def test_show_single_preference_poll_form_random_order(self):
        is_randomized = False
        models.PollOptions.objects.create(poll=self.poll, random_order=True)
        for i in range(0,2):
            resp = self.client.get(self.poll_url)
            resp1 = self.client.get(self.poll_url)
            is_randomized = is_randomized or remove_csfr_token(resp1)!=remove_csfr_token(resp)
        assert_that(is_randomized).is_true

    def test_show_single_preference_poll_form_fixed_order(self):
        models.PollOptions.objects.create(poll=self.poll, random_order=False)
        resp = self.client.get(self.poll_url)
        resp1 = self.client.get(self.poll_url)
        assert_that(remove_csfr_token(resp1)).is_equal_to(
            remove_csfr_token(resp))

    def test_submit_and_save_in_db(self):
        last_vote_old = models.SinglePreference.objects.last()
        preference_count_old = len(
            models.SinglePreference.objects.filter(alternative=1))
        resp = self.client.post(self.poll_url, data={
            'alternative': 1,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )

        last_vote = models.SinglePreference.objects.last()
        self.assertNotEqual(last_vote.id, last_vote_old.id)

        self.assertEqual(len(models.SinglePreference.objects.filter(
            alternative=1)), preference_count_old+1)

    def test_404_sondaggio_inesistente(self):
        url = reverse(self.URL, args=[100])
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
        url = reverse(self.URL, args=[empty_poll.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_if_submit_and_save_in_db(self):
        last_vote_old = models.SinglePreference.objects.last()
        resp = self.client.post(self.poll_url, {
            'alternative': 2
        })

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )
        last_vote = models.SinglePreference.objects.last()
        self.assertNotEqual(last_vote.id, last_vote_old.id)
        self.assertEqual(last_vote.alternative.id, 2)

    def test_creates_synthetic_MJ_vote(self):
        last_preference_old = models.MajorityPreference.objects.last()
        preference_count_old = len(models.MajorityPreference.objects.all())
        self.client.post(self.poll_url, data={
            'alternative': 1,
        })

        last_preference = models.MajorityPreference.objects.last()
        self.assertNotEqual(last_preference.id, last_preference_old.id)
        assert_that(last_preference.synthetic).is_equal_to(True)
        self.assertEqual(
            len(models.MajorityPreference.objects.all()), preference_count_old+1)

        for opinion in last_preference.majorityopinionjudgement_set.all():
            if opinion.alternative.id == 1:
                assert_that(opinion.grade).is_equal_to(5)
            else:
                assert_that(opinion.grade).is_equal_to(1)

    def test_revote(self):
        self.client.post(self.poll_url, data={
            'alternative': 1,
        })

        synthetic_vote = models.MajorityPreference.objects.last()
        revote_url = reverse('polls:vote_MJ', args=[self.poll.pk])
        resp = self.client.get(revote_url)
        self.assertEqual(resp.status_code, 200)
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
        assert_that(resp.status_code).is_equal_to(200)

        synthetic_vote = models.MajorityPreference.objects.get(id=synthetic_vote.id)
        assert_that(synthetic_vote.synthetic).is_equal_to(False)
        for opinion in synthetic_vote.majorityopinionjudgement_set.all():
            assert_that(opinion.grade).is_equal_to(1)


class TestVoteMajorityPreferenceView(TestCase):
    fixtures = ['polls.json']
    URL = 'polls:vote_MJ'

    def setUp(self) -> None:
        self.poll = models.Poll.objects.filter(
            default_type=models.Poll.PollType.MAJORITY_JUDGMENT).first()
        if self.poll is not None:
            self.poll_url = reverse(self.URL, args=[self.poll.pk])
            self.formset_class = pollforms.MajorityPreferenceFormSet.get_formset_class(
                self.poll.alternative_set.count())
            self.form = self.formset_class(
                queryset=self.poll.alternative_set.all())

    def test_show_majority_preference_poll_form(self):
        resp = self.client.get(self.poll_url)
        assert_that(resp.context['form'].forms).is_length(len(self.form.forms))
        assert_that(resp.status_code).is_equal_to(200)
        self.assertContains(
            response=resp,
            text=str(self.form.management_form)
        )
        self.assertContains(
            response=resp,
            text=self.poll.title
        )
        self.assertContains(
            response=resp,
            text=self.poll.text
        )

        f: pollforms.MajorityOpinionForm
        for f in self.form:
            self.assertContains(
                response=resp,
                text=f.fields['grade'].label
            )

    def test_show_majority_preference_poll_form_random_order(self):
        is_randomized = False
        models.PollOptions.objects.create(poll=self.poll, random_order=True)
        for _ in range(2):
            resp = self.client.get(self.poll_url)
            resp1 = self.client.get(self.poll_url)
            is_randomized = is_randomized or remove_csfr_token(resp1) != remove_csfr_token(resp)
        assert_that(is_randomized).is_true

    def test_show_majority_preference_poll_form_fixed_order(self):
        models.PollOptions.objects.create(poll=self.poll, random_order=False)
        resp = self.client.get(self.poll_url)
        resp1 = self.client.get(self.poll_url)
        assert_that(remove_csfr_token(resp1)).is_equal_to(
            remove_csfr_token(resp))

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
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )

        last_vote = models.MajorityPreference.objects.last()
        self.assertNotEqual(last_vote.id, last_vote_old.id)

        judgement: models.MajorityOpinionJudgement
        for judgement in last_vote.majorityopinionjudgement_set.all():
            self.assertEqual(judgement.grade, 1)

class TestVoteShultzePreferenceView(TestCase):
    fixtures = ['test_shultze.json']
    url = 'polls:vote_shultze'

    def setUp(self) -> None:
        self.poll = models.Poll.objects.first()
        if self.poll is None:
            raise Exception('No poll found')
        
        self.poll_url = reverse(self.url, args=[self.poll.pk])
        self.formset_class = pollforms.ShultzePreferenceFormSet.get_formset_class(self.poll.alternative_set.count())
        self.form = self.formset_class(queryset=self.poll.alternative_set.all())
    
    def test_show_shultze_poll_form(self):
        resp = self.client.get(self.poll_url)
        assert_that(resp.context['form'].forms).is_length(len(self.form.forms))
        assert_that(resp.status_code).is_equal_to(200)
        self.assertContains(
            response=resp,
            text=str(self.form.management_form)
        )
        self.assertContains(
            response=resp,
            text=self.poll.title
        )
        self.assertContains(
            response=resp,
            text=self.poll.text
        )

        f: pollforms.ShultzePreferenceFormSet
        for f in self.form:
            self.assertContains(
                response=resp,
                text=f.fields['order'].label
            )
        
    def test_submit_and_save_in_db(self):
        resp = self.client.post(self.poll_url, {
            'shultzeopinionjudgement_set-TOTAL_FORMS': 5,
            'shultzeopinionjudgement_set-INITIAL_FORMS': 0,
            'shultzeopinionjudgement_set-MIN_NUM_FORMS': 5,
            'shultzeopinionjudgement_set-MAX_NUM_FORMS': 5,
            'shultzeopinionjudgement_set-0-order': 4,
            'shultzeopinionjudgement_set-1-order': 1,
            'shultzeopinionjudgement_set-2-order': 5,
            'shultzeopinionjudgement_set-3-order': 3,
            'shultzeopinionjudgement_set-4-order': 2,
        })

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )

        last_vote = models.preference.ShultzePreference.objects.last()
        self.assertEqual(last_vote.shultzeopinionjudgement_set.count(), 5)

        self.assertEqual(last_vote.shultzeopinionjudgement_set.get(alternative__text='Lorem').order, 4)
        self.assertEqual(last_vote.shultzeopinionjudgement_set.get(alternative__text='Ipsum').order, 1)
        self.assertEqual(last_vote.shultzeopinionjudgement_set.get(alternative__text='dolor sit amet').order, 5)
        self.assertEqual(last_vote.shultzeopinionjudgement_set.get(alternative__text='consectetur adipiscing elit').order, 3)
        self.assertEqual(last_vote.shultzeopinionjudgement_set.get(alternative__text='Integer tristique').order, 2)

    def test_if_syntethic_vote_is_saved(self):
        resp = self.client.post(self.poll_url, {
            'shultzeopinionjudgement_set-TOTAL_FORMS': 5,
            'shultzeopinionjudgement_set-INITIAL_FORMS': 0,
            'shultzeopinionjudgement_set-MIN_NUM_FORMS': 5,
            'shultzeopinionjudgement_set-MAX_NUM_FORMS': 5,
            'shultzeopinionjudgement_set-0-order': 4,
            'shultzeopinionjudgement_set-1-order': 1,
            'shultzeopinionjudgement_set-2-order': 5,
            'shultzeopinionjudgement_set-3-order': 3,
            'shultzeopinionjudgement_set-4-order': 2,
        })

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )

        syntethic_vote = models.preference.MajorityPreference.objects.last()
        self.assertEqual(resp.client.session.get('preference_id'), syntethic_vote.id)
    
    def test_revote(self):
        self.test_if_syntethic_vote_is_saved()
        old_judgements = list(models.preference.MajorityPreference.objects.last().majorityopinionjudgement_set.all())

        resp = self.client.post(reverse('polls:vote_MJ', args=[1]), {
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

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )

        new_judgements = list(models.preference.MajorityPreference.objects.last().majorityopinionjudgement_set.all())
        self.assertNotEqual(old_judgements, new_judgements)
        for j in new_judgements:
            self.assertEqual(j.grade, 1)
        