from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.test import TestCase

from django.contrib.auth.models import User

from polls import forms as pollforms
from polls import models
from polls.models import Poll, Mapping, PollOptions

class FromCodeSessionCleanerTest(TestCase):

    code = "test"

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')

        self.poll = Poll()
        self.poll.title = 'Sondaggio di prova'
        self.poll.text = 'Sondaggio di prova'
        self.poll.start = timezone.now() - timedelta(weeks=1)
        self.poll.end = timezone.now() + timedelta(weeks=2)
        self.poll.author = self.user
        self.poll.author = self.user
        self.poll.default_type = 3
        self.poll.authentication_type = 1
        self.poll.save()
        self.poll.alternative_set.create(text='Alternativa di prova 1')
        self.poll.alternative_set.create(text='Alternativa di prova 2')

        Mapping.objects.create(poll=self.poll, code=self.code)
        PollOptions.objects.create(poll=self.poll)

        self.poll_url = reverse(
                'polls:vote_single_preference', args=[self.poll.pk])

    def test_clear_session_correctly(self):

        #per codice
        redirect_url = reverse('polls:access_poll', kwargs={'code': self.code})
        self.client.get(redirect_url)
        session = self.client.session
        from_code = session['from_code']
        self.assertTrue(from_code)

        #ritorno alla home
        home_page_url = reverse('polls:index')
        self.client.get(home_page_url)
        session = self.client.session
        self.assertFalse('from_code' in session)

        #senza codice
        home_page_url = reverse('polls:vote', kwargs={'id': self.poll.pk})
        self.client.get(home_page_url)
        session = self.client.session
        self.assertFalse('from_code' in session)


    def test_clear_session_code_on_revote(self):

        #per codice
        redirect_url = reverse('polls:access_poll', kwargs={'code': self.code})
        self.client.get(redirect_url)
        session = self.client.session
        from_code = session['from_code']
        self.assertTrue(from_code)


        resp = self.client.get(self.poll_url)
        self.assertEqual(resp.status_code, 200)

        alternative = models.Alternative.objects.filter(poll=self.poll.id).first()

        #post della risposta
        resp = self.client.post(self.poll_url, data={
            'alternative': alternative.pk,
        })

        self.assertEqual(resp.status_code, 200)

        session = self.client.session
        self.assertFalse('from_code' in session)

    






    

