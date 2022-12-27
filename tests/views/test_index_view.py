from django.test import Client, TestCase
from polls.models import SinglePreferencePoll
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

class IndexViewTest(TestCase):
    
    url = reverse('polls:index')

    def setUp(self):
        self.client = Client()
        self.poll = SinglePreferencePoll(title="Titolo test", text = "Sondaggio di prova",
            start = timezone.now(), end = timezone.now() + timedelta(weeks=1))
        self.poll.save()

    def test_sondaggi_attivi(self):
        self.poll.alternative_set.create(text = "Prova")

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.poll.title)
        
    def test_sondaggio_senza_scelte(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        
        #Per ora controllano se ci sono i bottoni "Vota" e "Risultati" associati alle card dei sondaggi
        self.assertNotContains(resp, "Vota")
        self.assertNotContains(resp, "Risultati")
    
    def test_nessun_sondaggio(self):
        self.poll.delete()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Vota")
        self.assertNotContains(resp, "Risultati")