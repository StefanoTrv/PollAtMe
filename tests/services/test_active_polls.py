from django.test import TestCase
from polls.services import ActivePollsService, SearchPollService
from django.core.exceptions import ObjectDoesNotExist
from polls.exceptions import PollWithoutAlternativesException
from polls.models import Poll
from assertpy import assert_that #type: ignore

class TestActivePollsService(TestCase):
    
    fixtures: list[str] = ['polls.json']

    def test_sondaggi_pref_singola_ordine_crescente(self):
        queryset = ActivePollsService().get_ordered_queryset(asc=False)
        excluded = Poll.objects.get(id=3)
        self.assertNotIn(excluded,queryset)
        assert_that(queryset).is_sorted(lambda x: x.text, reverse=True)
    
    def test_sondaggi_pref_singola_ordine_decrescente(self):
        queryset = ActivePollsService().get_ordered_queryset(asc=True)
        excluded = Poll.objects.get(id=3)
        self.assertNotIn(excluded,queryset)
        assert_that(queryset).is_sorted(lambda x: x.text, reverse=False)


class TestSearchPollService(TestCase):
    
    fixtures: list[str] = ['polls.json']

    def test_search_by_id(self):
        expected_poll = Poll.objects.get(id=1)
        poll = SearchPollService().search_by_id(1)
        assert_that(poll).is_equal_to(expected_poll)
        assert_that(poll.alternative_set).is_equal_to(expected_poll.alternative_set)
    
    def test_search_by_error(self):
        last_id = Poll.objects.all().order_by('-id').first().id
        self.assertRaises(ObjectDoesNotExist,SearchPollService().search_by_id,last_id+1)
        self.assertRaises(PollWithoutAlternativesException,SearchPollService().search_by_id,3)