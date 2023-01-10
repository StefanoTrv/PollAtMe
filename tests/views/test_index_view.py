from django.test import Client, TestCase
from polls.models import Poll
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

class IndexViewTest(TestCase):
    
    url = reverse('polls:index')

    def setUp(self):
        self.client = Client()
        self.poll = Poll(title="Titolo test", text = "Sondaggio di prova",
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


class SearchPollViewTest(TestCase):

    url = reverse('polls:search_poll')

    def test_pagina_default(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/search_poll.html')
        self.assertTemplateNotUsed(response, 'polls/includes/poll_list.html')
        self.assertTemplateUsed(response, 'polls/includes/search_form.html')
    
    def test_form_valido(self):
        response = self.client.post(self.url, {
            'title': '',
            'status': '',
            'type': '',
            'range_start_a': '',
            'range_start_b': '',
            'range_end_a': '',
            'range_end_b': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'polls/search_poll.html')
        self.assertTemplateUsed(response, 'polls/includes/poll_list.html')
        self.assertTemplateNotUsed(response, 'polls/includes/search_form.html')
    
    def test_form_non_valido(self):
        response = self.client.post(self.url, {
            'title': '',
            'status': '',
            'type': '',
            'range_start_a': '05/01/0000',
            'range_start_b': '',
            'range_end_a': '',
            'range_end_b': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'polls/search_poll.html')
        self.assertTemplateNotUsed(response, 'polls/includes/poll_list.html')
        self.assertTemplateUsed(response, 'polls/includes/search_form.html')