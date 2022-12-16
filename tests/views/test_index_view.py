from django.test import Client, TestCase
from polls.models import SinglePreferencePoll
from django.urls import reverse

class IndexViewTest(TestCase):
    
    url = reverse('polls:index')

    def setUp(self):
        self.client = Client()
        self.poll = SinglePreferencePoll(title="Titolo test", text = "Sondaggio di prova")
        self.poll.save()

    def test_sondaggi_attivi(self):
        self.poll.alternative_set.create(text = "Prova")

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.poll.title)
        
    def test_sondaggio_senza_scelte(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Non ci sono sondaggi attivi al momento")
    
    def test_nessun_sondaggio(self):
        self.poll.delete()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Non ci sono sondaggi attivi al momento")
    
    def test_cancellazione_sondaggio(self):
        self.poll.alternative_set.create(text = "Prova")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.poll.title)
        response = self.client.post(self.url, data={'delete_poll_id': self.poll.id})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.poll.title)