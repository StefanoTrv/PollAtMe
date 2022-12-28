from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import SinglePreferencePoll, MajorityOpinionPoll


class TestPollEditView(TestCase):

    def setUp(self) -> None:
        self.poll = SinglePreferencePoll()
        self.poll.title = "Sondaggio di prova"
        self.poll.text = "Sondaggio di prova"
        self.poll.start = timezone.now() + timedelta(weeks=1)
        self.poll.end = timezone.now() + timedelta(weeks=2)
        self.poll.save()
        self.poll.alternative_set.create(text="Alternativa di prova 1")
        self.poll.alternative_set.create(text="Alternativa di prova 2")
    
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



