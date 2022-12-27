from django.test import TestCase
from polls.services import ActivePollsService, SearchPollService
from django.core.exceptions import ObjectDoesNotExist
from polls.exceptions import PollWithoutAlternativesException
from polls.models import Poll
from assertpy import assert_that #type: ignore

class TestActivePollsService(TestCase):
    
    fixtures: list[str] = ['polls.json']

    def test_sondaggi_ordine_crescente(self):
        queryset = ActivePollsService().get_ordered_queryset(asc=True)
        excluded = Poll.objects.filter(id__in = [2, 3])
        
        # Esclude sondaggi senza alternative o non ancora attivi 
        self.assertNotIn(excluded, queryset)

        # Mostra prima i sondaggi attivi
        assert_that(queryset).is_sorted(lambda x: x.is_active(), reverse=True)
        assert_that([poll for poll in queryset if poll.is_active()]).is_sorted(lambda x: x.title)
        assert_that([poll for poll in queryset if not poll.is_active()]).is_sorted(lambda x: x.title)
    
    def test_sondaggi_ordine_decrescente(self):
        queryset = ActivePollsService().get_ordered_queryset(asc=False)
        excluded = Poll.objects.filter(id__in = [2, 3])
        
        # Esclude sondaggi senza alternative o non ancora attivi 
        self.assertNotIn(excluded, queryset)

        # Mostra prima i sondaggi attivi
        assert_that(queryset).is_sorted(lambda x: x.is_active(), reverse=True)
        assert_that([poll for poll in queryset if poll.is_active()]).is_sorted(lambda x: x.title, reverse=True)
        assert_that([poll for poll in queryset if not poll.is_active()]).is_sorted(lambda x: x.title, reverse=True)
        


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