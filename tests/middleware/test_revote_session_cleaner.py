from django.test import TestCase
from django.urls import reverse
from assertpy import assert_that # type: ignore

class RevoteSessionCleanerTest(TestCase):

    fixtures = ['polls.json']
    vote_url_sp = reverse('polls:vote_single_preference', args=[1])
    vote_url_sh = reverse('polls:vote_shultze', args=[6])

    def test_clears_revote_single_preference(self):
        response = self.client.post(self.vote_url_sp, data= {'alternative': 1})
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('polls:index'))
        assert_that(response.get('preference_id') is None)
        assert_that(response.get('alternative_sp') is None)
        assert_that(response.get('revote_type') is None)

    def test_clears_revote_schulze(self):
        response = self.client.post(self.vote_url_sh, data= {'alternative': 1})
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('polls:index'))
        assert_that(response.get('preference_id') is None)
        assert_that(response.get('sequence_shultze') is None)
        assert_that(response.get('revote_type') is None)