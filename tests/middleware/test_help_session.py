
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.test import TestCase

from django.contrib.auth.models import User

from polls import forms as pollforms
from polls import models

class NewPollSessionCleanerTest(TestCase):

    help_MJ = reverse('polls:explain_gm')
    help_SCH = reverse('polls:explain_sch')

    fixtures = ['polls.json']
    fixtures = ['polls.json']
    URL = 'polls:vote_single_preference'

    def setUp(self) -> None:
        self.poll = models.Poll.objects.first()
        if self.poll is not None:
            self.poll_url = reverse(
                'polls:vote_single_preference', args=[self.poll.pk])
            self.form = pollforms.SinglePreferenceForm(poll=self.poll)

    def test_session_help_MJ(self):
        self.client.post(self.poll_url, data={
            'alternative': 1,
        })

        revote_url = reverse('polls:vote_MJ', args=[self.poll.pk])
        resp = self.client.get(revote_url)
        session = self.client.session
        expectedId = session['preference_id']
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(self.help_MJ)
        session = self.client.session
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(session['preference_id'], expectedId)

    def test_session_to_help_Schultze(self):
        self.client.post(self.poll_url, data={
            'alternative': 1,
        })

        revote_url = reverse('polls:vote_MJ', args=[self.poll.pk])
        resp = self.client.get(revote_url)
        session = self.client.session
        expectedId = session['preference_id']
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(self.help_SCH)
        session = self.client.session
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(session['preference_id'], expectedId)

    
    