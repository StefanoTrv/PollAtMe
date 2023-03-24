from django.test import TestCase
from django.urls import reverse
from assertpy import assert_that # type: ignore

class RevoteSessionCleanerTest(TestCase):

    vote_url = reverse('polls:vote_MJ', args=[1])

    def test_clears_revote(self):
            self.client.post(self.vote_url, data= {'alternative_sp': 'Stracciatella', 'preference_id': '1'})
            response = self.client.get(self.vote_url)
            assert_that(response.get('preference_id') is None)
            assert_that(response.get('alternative_sp') is None)