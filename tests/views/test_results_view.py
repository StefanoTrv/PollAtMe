from django.test import Client, TestCase
from polls.models import SinglePreferencePoll, MajorityOpinionPoll, Alternative
from django.urls import reverse
from polls.services.preferenza_singola import SinglePreferencePollResultsService
from polls.services.giudizio_maggioritario import MajorityJudgementService

class ResultsViewTest(TestCase):
    
    fixtures: list[str] = ['polls.json']

    def test_preferenza_singola_mostra_alternative_con_voti_totali(self):
        url = reverse('polls:result', args=[1])
        results = {}
        poll = SinglePreferencePoll.objects.get(id = 1)
        for item in SinglePreferencePollResultsService().set_poll(poll).as_list():
            results[item['alternative']]=item['count']
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        for alternative in Alternative.objects.filter(poll = poll.id):
            self.assertContains(resp, alternative.text)
            self.assertContains(resp, results[alternative.text])

    def test_giudizio_maggioritario_mostra_alternative_in_classifica(self):
        url = reverse('polls:result', args=[4])
        results = {}
        for item in MajorityJudgementService().search_by_poll_id(4).get_classifica()['classifica']:
            results[item['alternative']]=item['place']
        poll = MajorityOpinionPoll.objects.get(id = 4)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        for alternative in Alternative.objects.filter(poll = poll.id):
            self.assertContains(resp, 'la scelta '+alternative.text+' è arrivata in posizione '+str(results[alternative.text]))