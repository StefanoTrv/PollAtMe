from django.test import TestCase
from django.urls import reverse
from assertpy import assert_that # type: ignore

class RevoteSessionCleanerTest(TestCase):

    vote_url = reverse('polls:vote_MJ')

    def test_clears_revote(self):
            self.client.post(self.vote_url, data= {'alternative_sp': ''})
            
            self.client.get(reverse('polls:index'))
            response = self.client.get(self.vote_url)
            assert_that(response.session.get('alternative_sp') is None)