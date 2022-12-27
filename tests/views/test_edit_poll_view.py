from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import SinglePreferencePoll


class TestPollEditView(TestCase):

    def setUp(self) -> None:
        self.poll = SinglePreferencePoll()
        self.poll.title = "Sondaggio di prova"
        self.poll.text = "Sondaggio di prova"
        self.poll.start = timezone.now() + timedelta(weeks=1)
        self.poll.end = timezone.now() + timedelta(weeks=2)
        self.poll.save()
        self.poll.alternative_set.create(text="Alternativa di prova")
    
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

