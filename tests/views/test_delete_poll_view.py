from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import Alternative, Poll, SinglePreferencePoll


class TestPollDeleteView(TestCase):

    def setUp(self) -> None:
        self.poll = SinglePreferencePoll()
        self.poll.title = "Sondaggio di prova"
        self.poll.text = "Sondaggio di prova"
        self.poll.start = timezone.now()
        self.poll.end = timezone.now() + timedelta(weeks=1)
        self.poll.save()
        self.poll.alternative_set.create(text="Alternativa di prova")
    
    def test_eliminazione(self):
        poll_id = self.poll.pk
        response = self.client.post(
            reverse('polls:delete_poll', kwargs={'pk': poll_id}),
        )

        assert_that(response.url).is_equal_to(reverse('polls:index'))
        assert_that(Poll.objects.get).raises(ObjectDoesNotExist).when_called_with(pk=poll_id)
        assert_that(Alternative.objects.filter(poll=poll_id)).is_length(0)
        assert_that(SinglePreferencePoll.objects.filter(poll_ptr_id=poll_id)).is_length(0)

