from django.test import TestCase
from django.urls import reverse
from assertpy import assert_that # type: ignore

class RevoteSessionCleanerTest(TestCase):

    fixtures = ['polls.json']
    vote_url = reverse('polls:vote_single_preference', args=[1])

    def test_clears_revote(self):
            response = self.client.post(self.vote_url, data= {'alternative': 1})
            self.assertEqual(response.status_code,200)
            response = self.client.get(reverse('polls:index'))
            assert_that(response.get('preference_id') is None)
            assert_that(response.get('alternative_sp') is None)