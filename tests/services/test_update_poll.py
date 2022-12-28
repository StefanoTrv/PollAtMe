from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.test import TestCase
from django.utils import timezone

from polls.models import Poll
from polls.services import update_poll


class TestUpdatePollService(TestCase):

    fixtures: list[str] = ['polls.json']

    def test_edit_poll(self):
        alternatives=['a test', 'b test', 'c test']
        poll = Poll.objects.filter(id=1)[0]
        time = timezone.now()
        update_poll(poll,title='TestUpdatePollService', text='text', alternatives=alternatives, 
            start_time=time, end_time=time + timedelta(weeks=1))
        poll = Poll.objects.filter(id=1)[0]
        assert_that(poll.title).is_equal_to('TestUpdatePollService')
        assert_that(poll.text).is_equal_to('text')
        assert_that(poll.alternative_set.all()).is_length(len(alternatives))
        for alt in poll.alternative_set.all():
            self.assertIn(alt.text,alternatives)
        assert_that(poll.start).is_equal_to(time)
        assert_that(poll.end).is_equal_to(time + timedelta(weeks=1))