from django.test import Client, TestCase
from polls.models import Poll
from django.urls import reverse

class IndexViewTest(TestCase):
    
    url = reverse('polls:index')

    def setUp(self):
        self.client = Client()
        self.poll = Poll(text = "Sondaggio di prova")
        self.poll.save()

    def test_sondaggi_attivi(self):

        self.poll.choice_set.create(choice_text = "Prova")

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.poll.text)
    
    def test_sondaggio_senza_scelte(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Non ci sono polls attive")
    
    def test_nessun_sondaggio(self):
        self.poll.delete()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Non ci sono polls attive")