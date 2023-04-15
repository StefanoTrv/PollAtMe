from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from polls.models import Poll, Mapping, PollOptions

# Test semplificati: molti aspetti vengono già testati relativamente alla creazione, che è praticamente la stessa pagina
class TestPollEditView(TestCase):

    def setUp(self) -> None:
        self.u = User.objects.create_user(username='test', password='test')
        self.poll = Poll()
        self.poll.title = 'Sondaggio di prova'
        self.poll.text = 'Sondaggio di prova'
        self.poll.start = timezone.now() + timedelta(weeks=1)
        self.poll.end = timezone.now() + timedelta(weeks=2)
        self.poll.author = self.u
        self.poll.save()
        self.poll.alternative_set.create(text='Alternativa di prova 1')
        self.poll.alternative_set.create(text='Alternativa di prova 2')
        self.poll.visibility = 1

        Mapping.objects.create(poll=self.poll, code="lorem")
        PollOptions.objects.create(poll=self.poll)

        self.client.login(username='test', password='test')
    
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
        self.assertTemplateUsed(response, 'polls/create_poll/main_page_edit.html')

        ##dati preinseriti
        assert_that(response.context['form'].initial['title']).is_equal_to('Sondaggio di prova')
        assert_that(response.context['form'].initial['default_type']).is_equal_to(Poll.PollType.MAJORITY_JUDGMENT)
        assert_that(response.context['form'].initial['text']).is_equal_to('Sondaggio di prova')


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
        self.assertTemplateUsed('polls/create_poll/summary_and_options_edit.html')
        assert_that(self.client.session.has_key('edit')).is_true()

        ##dati preesistenti
        assert_that(response.context['form'].initial['start']).is_equal_to(self.poll.start)
        assert_that(response.context['form'].initial['end']).is_equal_to(self.poll.end)
        assert_that(response.context['form'].initial['visibility'] == 1).is_true
        assert_that(response.context['mapping_form'].initial['code']).is_equal_to('lorem')
        assert_that(response.context['options_form'].initial['random_order']).is_equal_to(True)


        start = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        end = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'title': 'Lorem',
            'text': 'Ipsum',
            'default_type': 1,
            'start': start,
            'end': end,
            'author': self.u.id,
            'visibility': Poll.PollVisibility.PUBLIC.value,
            'authentication_type': Poll.PollAuthenticationType.FREE.value,
            'save': ''
        }
        response = self.client.post(url, data=data)
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse('polls:poll_created_success'))

        last_poll = Poll.objects.last()
        assert_that(last_poll.title).is_equal_to(data['title'])
        assert_that(last_poll.default_type).is_equal_to(data['default_type'])
        assert_that(last_poll.text).is_equal_to(data['text'])
        assert_that(last_poll.alternative_set.count()).is_equal_to(2)
        assert_that(last_poll.visibility).is_equal_to(Poll.PollVisibility.PUBLIC.value)
        assert_that(last_poll.mapping.code).is_not_equal_to('Lorem').is_length(6)

        alternatives = last_poll.alternative_set.all()
        expected_texts = ['Alternativa di prova 2', 'Alternativa di prova 3']
        for alt, text in zip(alternatives, expected_texts):
            assert_that(alt.text).is_equal_to(text)

    def test_edit_poll_after_start(self):
        url = reverse('polls:edit_poll', kwargs={'id': self.poll.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'polls/create_poll/main_page_edit.html')

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
            'author': self.u.id,
            'save': ''
        }
        
        self.poll.start = timezone.now() - timedelta(minutes=1)
        self.poll.save()
        
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 403)

