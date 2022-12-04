from django.test import TestCase
from polls.models import SinglePreferencePoll, SinglePreference
from polls.services import PollResultsService
from assertpy import assert_that #type: ignore


class TestPollResultsService(TestCase):

    def setUp(self) -> None:
        self.__poll = SinglePreferencePoll(title="Prova", text="Domanda di prova")
        self.__poll.save()
        self.__a1 = self.__poll.alternative_set.create(text="Risposta 1")
        self.__poll.alternative_set.create(text="Risposta 2")
        SinglePreference(poll=self.__poll, alternative=self.__a1).save()
        self.__service = PollResultsService().search_by_poll_id(self.__poll.id)
    
    def test_ascendant(self):
        l = self.__service.as_list()
        assert_that(l).is_sorted(lambda x: x['count'], reverse=True)

    def test_descendant(self):
        l = self.__service.as_list(False)
        assert_that(l).is_sorted(lambda x: x['count'], reverse=False)

    def test_if_error(self):
        self.__service = PollResultsService()
        self.assertRaises(AttributeError,self.__service.as_list,True)
        self.assertRaises(AttributeError,self.__service.as_list,False)
