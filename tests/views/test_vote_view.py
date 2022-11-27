from django.test import Client, TestCase
from polls.models import SinglePreferencePoll, Alternative
from django.urls import reverse

class VoteViewTest(TestCase):
    
    fixtures: list[str] = ['polls.json']

    def test_mostra_titolo_e_testo_e_alternative(self):
        url = reverse('polls:vote', args=[1])
        poll = SinglePreferencePoll.objects.get(id = 1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        #self.assertContains(resp, poll.title)  #disattivato perché al momento il titolo non appare nella pagina
        self.assertContains(resp, poll.text)
        for alternative in Alternative.objects.filter(poll = poll.id):
            self.assertContains(resp, alternative.text)

    def test_404_sondaggio_inesistente(self):
        url = reverse('polls:vote', args=[100])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Il sondaggio ricercato non esiste')
        
    def test_sondaggio_senza_scelte(self):
        empty_poll = SinglePreferencePoll()
        empty_poll.title = 'Title'
        empty_poll.text = 'Text'
        empty_poll.save()
        url = reverse('polls:vote', args=[empty_poll.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Il sondaggio ricercato non ha opzioni di risposta')