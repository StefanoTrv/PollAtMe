from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from polls.models import Alternative, Poll


class TestPollDeleteView(TestCase):

    def setUp(self) -> None:
        self.poll = Poll()
        self.poll.default_type = Poll.PollType.SINGLE_PREFERENCE
        self.poll.title = "Sondaggio di prova"
        self.poll.text = "Sondaggio di prova"
        self.poll.start = timezone.now() + timedelta(weeks=1)
        self.poll.end = timezone.now() + timedelta(weeks=2)
        self.poll.author = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        self.poll.save()
        self.poll.alternative_set.create(text="Alternativa di prova")
    
    def test_eliminazione(self):
        poll_id = self.poll.pk
        response = self.client.post(
            reverse('polls:delete_poll', kwargs={'pk': poll_id}),
        )

        assert_that(response.url).is_equal_to(reverse('polls:personal_polls'))
        assert_that(Poll.objects.get).raises(ObjectDoesNotExist).when_called_with(pk=poll_id)
        assert_that(Alternative.objects.filter(poll=poll_id)).is_length(0)

    def test_forbidden(self):
        self.poll.start = timezone.now() - timedelta(days=1)
        self.poll.save()

        poll_id = self.poll.pk
        response = self.client.post(
            reverse('polls:delete_poll', kwargs={'pk': poll_id}),
        )
        assert_that(response.status_code).is_equal_to(403)

