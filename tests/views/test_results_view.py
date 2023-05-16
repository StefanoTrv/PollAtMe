from django.test import TestCase
from assertpy import assert_that #type: ignore
from polls.models import Poll, Alternative
from django.urls import reverse
from polls.services.preferenza_singola import SinglePreferencePollResultsService
from polls.services.giudizio_maggioritario import MajorityJudgementService
from polls.services.shultze_calculator import ShultzeCalculator, calculate_sequences_from_db

class ResultsViewTest(TestCase):
    
    fixtures: list[str] = ['polls.json']

    def test_preferenza_singola_mostra_alternative_con_voti_totali(self):
        url = reverse('polls:result_single_preference', args=[1])
        results = {}
        poll = Poll.objects.get(id = 1)
        for item in SinglePreferencePollResultsService().set_poll(poll).as_list():
            results[item['text']]=item['count']
        resp = self.client.get(url)
        assert_that(resp.status_code).is_equal_to(200)
        for alternative in Alternative.objects.filter(poll = poll.id):
            self.assertContains(resp, alternative.text.upper())
            self.assertContains(resp, results[alternative.text])

    
    def test_giudizio_maggioritario_mostra_alternative_in_classifica(self):
        url = reverse('polls:result_MJ', args=[2])
        results = {}
        poll = Poll.objects.get(id=2)
        for item in MajorityJudgementService(poll).get_classifica()['classifica']:
            results[item['alternative']]=item['place']
        resp = self.client.get(url)
        assert_that(resp.status_code).is_equal_to(200)
        for alternative in poll.alternative_set.all():
            self.assertContains(resp, alternative.text.upper())
            self.assertContains(resp, alternative.text+'-'+str(results[alternative.text]))
    
class ResultViewShultze(TestCase):
    fixtures: list[str] = ['test_shultze.json']

    def test_shultze_mostra_alternative_in_classifica(self):
        url = reverse('polls:result_shultze', args=[1])
        resp = self.client.get(url)
        assert_that(resp.status_code).is_equal_to(200)
        poll = Poll.objects.get(id=1)
        calculator = ShultzeCalculator(calculate_sequences_from_db(poll))
        calculator.calculate()

        for alternative, pos in calculator.rankings:
            self.assertContains(resp, alternative.text.upper())
            self.assertContains(resp, f"{alternative.text}-{pos}")