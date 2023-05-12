from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from polls.views import IndexView, SinglePreferenceResultView, MajorityJudgementResultView, VoteSinglePreferenceView, VoteMajorityJudgmentView
from polls.views.help_view import ExplanationGMView, ExplanationSchView

class UrlsTest(SimpleTestCase): #usiamo SimpleTestCase perchè non facciamo riferimento al db

    def test_index_resolves(self):
        url = reverse('polls:index')
        self.assertEqual(resolve(url).func.view_class, IndexView)

    def test_vote_resolves_vote(self):
        url = reverse('polls:vote_single_preference', args = [1])
        self.assertEqual(resolve(url).func.view_class, VoteSinglePreferenceView)
        
        url = reverse('polls:vote_MJ', args = [1])
        self.assertEqual(resolve(url).func.view_class, VoteMajorityJudgmentView)

    def test_result_resolves(self):
        url = reverse('polls:result_single_preference', args = [1])
        self.assertEqual(resolve(url).func.view_class, SinglePreferenceResultView)

        url = reverse('polls:result_MJ', args = [1])
        self.assertEqual(resolve(url).func.view_class, MajorityJudgementResultView)
        

class TestResultRedirect(TestCase):
    fixtures = ['polls.json']
    URL = 'polls:result'

    def test_redirect_to_single_preference(self):
        resp = self.client.get(reverse(self.URL,args=[1]))
        self.assertRedirects(resp, reverse('polls:result_single_preference',args=[1]))

    def test_redirect_to_majority_judgment(self):
        resp = self.client.get(reverse(self.URL,args=[2]))
        self.assertRedirects(resp, reverse('polls:result_MJ',args=[2]))


class TestVoteRedirect(TestCase):
    fixtures = ['polls.json']
    URL = 'polls:vote'

    def test_redirect_to_single_preference(self):
        resp = self.client.get(reverse(self.URL,args=[1]))
        self.assertRedirects(resp, reverse('polls:vote_single_preference',args=[1]))

    def test_redirect_to_majority_judgment(self):
        resp = self.client.get(reverse(self.URL,args=[2]))
        self.assertRedirects(resp, reverse('polls:vote_MJ',args=[2]))
    
    def test_redirect_to_shultze(self):
        resp = self.client.get(reverse(self.URL,args=[6]))
        self.assertRedirects(resp, reverse('polls:vote_shultze',args=[6]))


class TestHelpPages(TestCase):

    URL_GM = 'polls:explain_gm'
    URL_SCH = 'polls:explain_sch'


    def test_HelpGiudizioMaggioritario(self):

        self.assertEqual(resolve(reverse(self.URL_GM)).func.view_class, ExplanationGMView)
        resp = self.client.get(reverse(self.URL_GM))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<!--TAG TEST explain_GM-->')



    def test_HelpSchultze(self):

        self.assertEqual(resolve(reverse(self.URL_SCH)).func.view_class, ExplanationSchView)
        resp = self.client.get(reverse(self.URL_SCH))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<!--TAG TEST explain_SCH-->')
