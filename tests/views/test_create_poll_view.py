from django.test import Client, TestCase
from django.urls import reverse

from polls.models import SinglePreferencePoll

class CreatePollViewTest(TestCase):
    
    url = reverse('polls:create_poll')

    def test_aggiunta_poll_preferenza_singola(self):
        response = self.client.post(self.url, data={'poll_title': 'titolo', 'poll_text': 'testo della domanda', 'alternative_count': '3'})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alternativa 3')
        response = self.client.post(self.url, data = {'alternative1': 'prima alternativa', 'alternative2': 'seconda alternativa', 'alternative3': 'terza alternativa'})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.url, data = {'poll_type': 'Preferenza singola'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'Perfetto! Il tuo sondaggio è stato creato.')
        last_poll = SinglePreferencePoll.objects.last()
        self.assertIsNotNone(last_poll)
        self.assertEqual(last_poll.title,'titolo')
        self.assertEqual(last_poll.text,'testo della domanda')
        self.assertEqual(len(last_poll.alternative_set.all()),3)
        alternatives = ['prima alternativa', 'seconda alternativa', 'terza alternativa']
        for alternative in last_poll.alternative_set.all():
            self.assertIn(alternative.text,alternatives)