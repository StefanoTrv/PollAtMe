from django.test import SimpleTestCase
from django.urls import reverse, resolve
from polls.views import IndexView, SinglePreferenceListView, VotingView

class UrlsTest(SimpleTestCase): #usiamo SimpleTestCase perchè non facciamo riferimento al db

    def test_index_resolves(self):
        url = reverse('polls:index')
        self.assertEqual(resolve(url).func.view_class, IndexView)

    def test_vote_resolves_vote(self):
        url = reverse('polls:vote', args = [1])
        self.assertEqual(resolve(url).func.view_class, VotingView)

    def test_result_resolves(self):
        url = reverse('polls:result', args = [1])
        self.assertEqual(resolve(url).func.view_class, SinglePreferenceListView)
        