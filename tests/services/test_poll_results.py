from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.test import TestCase
from django.utils import timezone

from polls.models import SinglePreference, Poll
from polls.services import SinglePreferencePollResultsService


class TestPollResultsService(TestCase):

    def setUp(self) -> None:
        self.__poll = Poll(title="Prova", text="Domanda di prova", default_type=Poll.PollType.SINGLE_PREFERENCE,
            start=timezone.now(), end=timezone.now() + timedelta(weeks=1))
        self.__poll.save()
        self.__a1 = self.__poll.alternative_set.create(text="Risposta 1")
        self.__poll.alternative_set.create(text="Risposta 2")
        SinglePreference(poll=self.__poll, alternative=self.__a1).save()
        self.__service = SinglePreferencePollResultsService().set_poll(self.__poll)
    
    def test_ascendant(self):
        l = self.__service.as_list()
        assert_that(l).is_sorted(lambda x: x['count'], reverse=True)

    def test_descendant(self):
        l = self.__service.as_list(False)
        assert_that(l).is_sorted(lambda x: x['count'], reverse=False)

    def test_if_error(self):
        self.__service = SinglePreferencePollResultsService()
        self.assertRaises(AttributeError,self.__service.as_list,True)
        self.assertRaises(AttributeError,self.__service.as_list,False)
