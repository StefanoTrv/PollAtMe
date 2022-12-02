from django.test import Client, TestCase
from polls.models import SinglePreferencePoll, Alternative
from django.urls import reverse
from polls.services.poll_results import PollResultsService

class ResultsViewTest(TestCase):
    
    fixtures: list[str] = ['polls.json']

    def test_mostra_alternative_con_voti_totali(self):
        url = reverse('polls:result', args=[1])
        results = {}
        for item in PollResultsService().search_by_poll_id(1).as_list():
            results[item['alternative']]=item['count']
        poll = SinglePreferencePoll.objects.get(id = 1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        for alternative in Alternative.objects.filter(poll = poll.id):
            self.assertContains(resp, 'la scelta '+alternative.text+' ha ottenuto '+str(results[alternative.text])+' voti')