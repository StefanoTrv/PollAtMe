from assertpy import assert_that  # type: ignore
from django.test import Client, TestCase
from polls.models import Poll
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth.models import User

class IndexViewTest(TestCase):
    
    url = reverse('polls:index')

    def setUp(self):
        self.u = User.objects.create_user(username='test')
        self.poll = Poll(
            title="Titolo test", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u
        )
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


class ClosePollViewTest(TestCase):
    
    URL = 'polls:personal_polls'

    def setUp(self):
        self.u = User.objects.create_user(username='test', password='test')
        self.poll1 = Poll(
            title="Tutti possono vedere i risultati", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u,
            results_restriction = Poll.PollResultsRestriction.ALL
        )
        self.poll1.save()
        self.poll2 = Poll(
            title="Solo il creatore può vedere i risultati", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u,
            results_restriction = Poll.PollResultsRestriction.AUTHOR
        )
        self.poll2.save()
        self.poll3 = Poll(
            title="Nessuno può vedere i risultati", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u,
            results_restriction = Poll.PollResultsRestriction.NOBODY
        )
        self.poll3.save()

    def test_chiusura_all(self):
        response = self.client.post(reverse('polls:close_poll', kwargs={'id': self.poll1.pk}))
        assert_that(self.poll1.end).is_not_equal_to(timezone.now())
        response = self.client.get(reverse(self.URL))
        assert_that(response == 'polls:personal_polls')

    def test_chiusura_only_creator(self):
        response = self.client.post(reverse('polls:close_poll', kwargs={'id': self.poll2.pk}))
        assert_that(self.poll2.end).is_not_equal_to(timezone.now())
        response = self.client.get(reverse(self.URL))
        assert_that(response == 'polls:personal_polls')

    def test_chiusura_nobody(self):
        response = self.client.post(reverse('polls:close_poll', kwargs={'id': self.poll3.pk}))
        assert_that(self.poll3.end).is_not_equal_to(timezone.now())
        response = self.client.get(reverse(self.URL))
        assert_that(response == 'polls:personal_polls')