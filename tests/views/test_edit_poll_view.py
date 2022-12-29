from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import SinglePreferencePoll, MajorityOpinionPoll, Poll

# Test semplificati: molti aspetti vengono già testati relativamente alla creazione, che è praticamente la stessa pagina
class TestPollEditView(TestCase):

    def setUp(self) -> None:
        self.poll = SinglePreferencePoll()
        self.poll.title = 'Sondaggio di prova'
        self.poll.text = 'Sondaggio di prova'
        self.poll.start = timezone.now() + timedelta(weeks=1)
        self.poll.end = timezone.now() + timedelta(weeks=2)
        self.poll.save()
        self.poll.alternative_set.create(text='Alternativa di prova 1')
        self.poll.alternative_set.create(text='Alternativa di prova 2')
    
    def test_mostra_pagina_edit(self):
        response = self.client.get(
            reverse('polls:edit_poll', kwargs={'id': self.poll.pk}),
        )

        assert_that(response.status_code).is_equal_to(200)

    def test_forbidden(self):
        self.poll.start = timezone.now() - timedelta(days=1)
        self.poll.save()

        poll_id = self.poll.pk
        response = self.client.post(
            reverse('polls:edit_poll', kwargs={'id': poll_id}),
        )
        assert_that(response.status_code).is_equal_to(403)

    # bug #146
    def test_change_poll_type(self):
        assert_that(SinglePreferencePoll.objects.all()).is_not_empty()
        assert_that(MajorityOpinionPoll.objects.all()).is_empty()
        url = reverse('polls:edit_poll', kwargs={'id': self.poll.pk})
        title = self.poll.title
        self.client.get(url)
        response = self.client.post(url, data = {
            'poll_title': self.poll.title,
            'poll_type': 'Giudizio maggioritario',
            'poll_text': self.poll.text,
            'hidden_alternative_count': len(self.poll.alternative_set.all()),
            'alternative1': self.poll.alternative_set.all()[0],
            'alternative2': self.poll.alternative_set.all()[1]
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data={
            'start_time': self.poll.start,
            'end_time': self.poll.end
        })
        self.assertEqual(response.status_code, 200)
        assert_that(SinglePreferencePoll.objects.all()).is_empty()
        assert_that(MajorityOpinionPoll.objects.all()).is_not_empty()
        assert_that(MajorityOpinionPoll.objects.last().title).is_equal_to(title)

    def test_edit_poll(self):
        start_time=timezone.now()
        end_time=timezone.now()+timedelta(weeks=1)
        data={
            'poll_title': 'titolo',
            'poll_type': 'Giudizio maggioritario',
            'poll_text': 'testo della domanda',
            'hidden_alternative_count': '3',
            'alternative1': 'prima alternativa',
            'alternative2': 'seconda alternativa', 
            'alternative3': 'terza alternativa'
        }
        url = reverse('polls:edit_poll', kwargs={'id': self.poll.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alternativa di prova 2')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data['alternative3'])
        response = self.client.post(url, data={
            'start_time': start_time,
            'end_time': end_time
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'Fatto! Il tuo sondaggio è stato modificato.')
        last_poll = Poll.objects.last()
        self.assertIsNotNone(last_poll)
        self.assertEqual(last_poll.title,data['poll_title'])
        assert_that(last_poll.get_type()).is_equal_to(data['poll_type'])
        self.assertEqual(last_poll.text,data['poll_text'])
        self.assertEqual(len(last_poll.alternative_set.all()),3)
        assert_that(last_poll.start).is_equal_to(start_time)
        assert_that(last_poll.end).is_equal_to(end_time)
        alternatives = [data['alternative1'], data['alternative2'], data['alternative3']]
        for alternative in last_poll.alternative_set.all():
            self.assertIn(alternative.text,alternatives)

    def test_edit_poll_after_start(self):
        
        start_time=timezone.now()
        end_time=timezone.now() + timedelta(weeks=1)
        data={
            'poll_title': 'titolo',
            'poll_type': 'Giudizio maggioritario',
            'poll_text': 'testo della domanda',
            'hidden_alternative_count': '3',
            'alternative1': 'prima alternativa',
            'alternative2': 'seconda alternativa', 
            'alternative3': 'terza alternativa'
        }
        url = reverse('polls:edit_poll', kwargs={'id': self.poll.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alternativa di prova 2')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data['alternative3'])
        
        self.poll.start = timezone.now() - timedelta(minutes=1)
        self.poll.save()
        
        response = self.client.post(url, data={
            'start_time': start_time,
            'end_time': end_time
        })
        self.assertEqual(response.status_code, 403)

