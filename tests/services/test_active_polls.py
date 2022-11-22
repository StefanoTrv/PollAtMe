from django.test import TestCase
from polls.services import ActivePollsService, SearchPollService
from django.core.exceptions import ObjectDoesNotExist
from polls.exceptions import PollWithoutChoicesException
from polls.models import Poll
from assertpy import assert_that #type: ignore

class TestActivePollsService(TestCase):
    
    fixtures: list[str] = ['polls.json']

    def test_get_ordered_queryset_ascendant(self):
        queryset = ActivePollsService().get_ordered_queryset(asc=False)
        excluded = Poll.objects.get(id=3)
        assert_that(queryset).does_not_contain(excluded).is_sorted(lambda x: x.text, reverse=True)
    
    def test_get_ordered_queryset_descendant(self):
        queryset = ActivePollsService().get_ordered_queryset(asc=True)
        excluded = Poll.objects.get(id=3)
        assert_that(queryset).does_not_contain(excluded).is_sorted(lambda x: x.text, reverse=False)


class TestSearchPollService(TestCase):
    
    fixtures: list[str] = ['polls.json']

    def test_search_by_id(self):
        expected_poll = Poll.objects.get(id=1)
        poll = SearchPollService().search_by_id(1)
        assert_that(poll).is_equal_to(expected_poll)
        assert_that(poll.choice_set).is_equal_to(expected_poll.choice_set)
    
    def test_search_by_error(self):
        assert_that(SearchPollService().search_by_id).raises(ObjectDoesNotExist).when_called_with(4)
        assert_that(SearchPollService().search_by_id).raises(PollWithoutChoicesException).when_called_with(3)