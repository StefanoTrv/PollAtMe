from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.test import TestCase
from django.utils import timezone

from polls.models import Poll
from polls.services import (add_majority_judgment_poll,
                            add_single_preference_poll)


class TestAddPollsServices(TestCase):

    def test_add_single_preference_poll(self):
        alternatives=['a', 'b', 'c']
        add_single_preference_poll(title='TestAddPollsServices', text='text', alternatives=alternatives, 
            start=timezone.now(), end=timezone.now() + timedelta(weeks=1))
        poll = Poll.objects.last()
        assert_that(poll.title).is_equal_to('TestAddPollsServices')
        assert_that(poll.text).is_equal_to('text')
        assert_that(poll.alternative_set.all()).is_length(len(alternatives))
        for alt in poll.alternative_set.all():
            self.assertIn(alt.text,alternatives)

    def test_add_majority_judgment_poll(self):
        alternatives=['a', 'b', 'c']
        add_majority_judgment_poll(title='TestAddPollsServices', text='text', alternatives=alternatives,
            start=timezone.now(), end=timezone.now() + timedelta(weeks=1))
        poll = Poll.objects.last()
        assert_that(poll.title).is_equal_to('TestAddPollsServices')
        assert_that(poll.text).is_equal_to('text')
        assert_that(poll.alternative_set.all()).is_length(len(alternatives))
        for alt in poll.alternative_set.all():
            self.assertIn(alt.text,alternatives)