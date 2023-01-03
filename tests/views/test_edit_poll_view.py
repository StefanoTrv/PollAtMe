from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import SinglePreferencePoll, Poll

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

    def test_edit_poll(self):
        url = reverse('polls:edit_poll', kwargs={'id': self.poll.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_poll/main_page_edit.html')

        data={
            'title': 'Lorem',
            'text': 'Ipsum',
            'default_type': 1,
            'form-TOTAL_FORMS': 3,
            'form-INITIAL_FORMS': self.poll.alternative_set.count(),
            'form-MIN_NUM_FORMS': 2,
            'form-MAX_NUM_FORMS': 10,
        }
        for i, alt in enumerate(self.poll.alternative_set.all()):
            data = data | {
                f'form-{i}-text': alt.text,
                f'form-{i}-id': alt.id,
                f'form-{i}-DELETE': '',
            }
        data = data | {
            'form-2-text': 'Alternativa di prova 3',
            'form-2-id': '',
            'form-2-DELETE': ''
        }
        data['form-0-DELETE'] = True

        response = self.client.post(url, data=data | {'summary': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed('create_poll/summary_and_options_edit.html')
        assert_that(self.client.session.has_key('edit')).is_true()

        start = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        end = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'title': 'Lorem',
            'text': 'Ipsum',
            'default_type': 1,
            'start': start,
            'end': end,
            'save': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_poll_success.html')

        last_poll = Poll.objects.last()
        assert_that(last_poll.title).is_equal_to(data['title'])
        assert_that(last_poll.default_type).is_equal_to(data['default_type'])
        assert_that(last_poll.text).is_equal_to(data['text'])
        assert_that(last_poll.alternative_set.count()).is_equal_to(2)

        alternatives = last_poll.alternative_set.all()
        expected_texts = ['Alternativa di prova 2', 'Alternativa di prova 3']
        for alt, text in zip(alternatives, expected_texts):
            assert_that(alt.text).is_equal_to(text)

    def test_edit_poll_after_start(self):
        
        url = reverse('polls:edit_poll', kwargs={'id': self.poll.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_poll/main_page_edit.html')

        data={
            'title': 'Lorem',
            'text': 'Ipsum',
            'default_type': 1,
            'form-TOTAL_FORMS': 3,
            'form-INITIAL_FORMS': self.poll.alternative_set.count(),
            'form-MIN_NUM_FORMS': 2,
            'form-MAX_NUM_FORMS': 10,
        }
        for i, alt in enumerate(self.poll.alternative_set.all()):
            data = data | {
                f'form-{i}-text': alt.text,
                f'form-{i}-id': alt.id,
                f'form-{i}-DELETE': '',
            }
        data = data | {
            'form-2-text': 'Alternativa di prova 3',
            'form-2-id': '',
            'form-2-DELETE': ''
        }
        data['form-0-DELETE'] = True

        response = self.client.post(url, data=data | {'summary': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed('create_poll/summary_and_options_edit.html')
        assert_that(self.client.session.has_key('edit')).is_true()

        start = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        end = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'title': 'Lorem',
            'text': 'Ipsum',
            'default_type': 1,
            'start': start,
            'end': end,
            'save': ''
        }
        
        self.poll.start = timezone.now() - timedelta(minutes=1)
        self.poll.save()
        
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 403)

