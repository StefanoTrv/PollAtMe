from datetime import datetime
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
        self.u1 = User.objects.create_user(username='test1', password='test1')
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
        self.a1 = self.poll1.alternative_set.create(text="Risposta 1")
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
        self.a1 = self.poll2.alternative_set.create(text="Risposta 1")
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
        self.a1 = self.poll3.alternative_set.create(text="Risposta 1")


    def test_close_poll_all_creator(self):
        self.client.login(username="test", password="test")
        response = self.client.post(reverse('polls:close_poll', kwargs={'id': self.poll1.pk}))
        assert_that(Poll.objects.get(pk=self.poll1.pk).end).is_less_than(datetime.now().astimezone())
        assert_that(response.url).is_equal_to(reverse(self.URL))

    def test_close_poll_all_creator_fails(self):
        self.client.login(username="test1", password="test1")
        response = self.client.post(reverse('polls:close_poll', kwargs={'id': self.poll1.pk}))
        assert_that(Poll.objects.get(pk=self.poll1.pk).end).is_greater_than(datetime.now().astimezone())
        assert_that(response.status_code).is_equal_to(403)
        
    def test_close_poll_only_creator_fails(self):
        self.client.login(username="test1", password="test1")
        response = self.client.post(reverse('polls:close_poll', kwargs={'id': self.poll2.pk}))
        assert_that(Poll.objects.get(pk=self.poll2.pk).end).is_greater_than(datetime.now().astimezone())
        assert_that(response.status_code).is_equal_to(403)

    def test_close_poll_nobody_creator(self):
        self.client.login(username="test", password="test")
        response = self.client.post(reverse('polls:close_poll', kwargs={'id': self.poll3.pk}))
        assert_that(Poll.objects.get(pk=self.poll3.pk).end).is_less_than(datetime.now().astimezone())
        assert_that(response.url).is_equal_to(reverse(self.URL))

    def test_close_poll_nobody_creator_fails(self):
        self.client.login(username="test1", password="test1")
        response = self.client.post(reverse('polls:close_poll', kwargs={'id': self.poll1.pk}))
        assert_that(Poll.objects.get(pk=self.poll1.pk).end).is_greater_than(datetime.now().astimezone())
        assert_that(response.status_code).is_equal_to(403)
