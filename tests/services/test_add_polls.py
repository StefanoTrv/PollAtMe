from django.test import TestCase
from polls.models import Poll
from polls.services import add_single_preference_poll, add_majority_judgment_poll
from assertpy import assert_that #type: ignore

class TestAddPollsServices(TestCase):

    def test_add_single_preference_poll(self):
        alternatives=['a', 'b', 'c']
        add_single_preference_poll(title='TestAddPollsServices', text='text', alternatives=alternatives)
        poll = Poll.objects.last()
        self.assertEquals(poll.title,'TestAddPollsServices')
        self.assertEquals(poll.text,'text')
        self.assertEquals(len(poll.alternative_set.all()),len(alternatives))
        for alt in poll.alternative_set.all():
            self.assertIn(alt.text,alternatives)

    def test_add_majority_judgment_poll(self):
        alternatives=['a', 'b', 'c']
        add_majority_judgment_poll(title='TestAddPollsServices', text='text', alternatives=alternatives)
        poll = Poll.objects.last()
        self.assertEquals(poll.title,'TestAddPollsServices')
        self.assertEquals(poll.text,'text')
        self.assertEquals(len(poll.alternative_set.all()),len(alternatives))
        for alt in poll.alternative_set.all():
            self.assertIn(alt.text,alternatives)