from django.test import TestCase
from polls.services import ActivePollsService, SearchPollService
from django.core.exceptions import ObjectDoesNotExist
from polls.exceptions import PollWithoutAlternativesException
from polls.models import Poll
from assertpy import assert_that #type: ignore
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

class TestActivePollsService(TestCase):
    
    def setUp(self) -> None:
        polls = [
            {'title': 'A', 'text': 'A', 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1)},  # concluso   
            {'title': 'B', 'text': 'B', 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1)},  # concluso
            {'title': 'C', 'text': 'C', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2)},  # attivo
            {'title': 'D', 'text': 'D', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2)},  # attivo
            {'title': 'E', 'text': 'E', 'start': timezone.now() + timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2)},  # non ancora attivo
            {'title': 'F', 'text': 'F', 'start': timezone.now(), 'end': timezone.now()},  # senza opzioni
        ]

        for p_dict in polls:
            Poll.objects.create(**p_dict)
        
        for poll in Poll.objects.filter(~Q(title='F')):
            poll.alternative_set.create(text="Prova1")
            poll.alternative_set.create(text="Prova2")

    def test_sondaggi_ordine_crescente(self):
        queryset = ActivePollsService().get_ordered_queryset()
        excluded = Poll.objects.filter(Q(title__in = ['E', 'F']))
        
        # Esclude sondaggi senza alternative o non ancora attivi 
        for poll in excluded:
            assert_that(queryset).does_not_contain(poll)
        
        # Mostra prima i sondaggi attivi
        assert_that(queryset).is_sorted(lambda x: x.is_active(), reverse=True)
        assert_that([poll for poll in queryset if poll.is_active()]).is_sorted(lambda x: x.title)
        assert_that([poll for poll in queryset if not poll.is_active()]).is_sorted(lambda x: x.title)
        
    
    def test_sondaggi_ordine_decrescente(self):
        queryset = ActivePollsService().get_ordered_queryset(desc=True)
        excluded = Poll.objects.filter(Q(title__in = ['E', 'F']))
        
        # Esclude sondaggi senza alternative o non ancora attivi 
        for poll in excluded:
            assert_that(queryset).does_not_contain(poll)
        
        # Mostra prima i sondaggi attivi
        assert_that(queryset).is_sorted(lambda x: x.is_active(), reverse=True)
        assert_that([poll for poll in queryset if poll.is_active()]).is_sorted(lambda x: x.title, reverse=True)
        assert_that([poll for poll in queryset if not poll.is_active()]).is_sorted(lambda x: x.title, reverse=True)
    
    def test_order_by_text(self):
        queryset = ActivePollsService().get_ordered_queryset(by_field='text')
        assert_that(queryset).is_sorted(lambda x: x.is_active(), reverse=True)
        assert_that([poll for poll in queryset if poll.is_active()]).is_sorted(lambda x: x.text)
        assert_that([poll for poll in queryset if not poll.is_active()]).is_sorted(lambda x: x.text)

class TestSearchPollService(TestCase):
    
    def setUp(self) -> None:
        polls = [
            {'title': 'A', 'text': 'A', 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1)},  # concluso   
            {'title': 'B', 'text': 'B', 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1)},  # concluso
            {'title': 'C', 'text': 'C', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2)},  # attivo
            {'title': 'D', 'text': 'D', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2)},  # attivo
            {'title': 'E', 'text': 'E', 'start': timezone.now() + timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2)},  # non ancora attivo
            {'title': 'F', 'text': 'F', 'start': timezone.now(), 'end': timezone.now()},  # senza opzioni
        ]

        for p_dict in polls:
            p = Poll(**p_dict)
            p.save()
        
        for poll in Poll.objects.filter(~Q(title='F')):
            poll.alternative_set.create(text="Prova1")
            poll.alternative_set.create(text="Prova2")
        
        print("done")

    def test_search_by_id(self):
        expected_poll = Poll.objects.get(title='A')
        poll = SearchPollService().search_by_id(expected_poll.id)
        assert_that(poll).is_equal_to(expected_poll)
        assert_that(poll.alternative_set).is_equal_to(expected_poll.alternative_set)
    
    def test_search_by_error(self):
        last_id = Poll.objects.all().order_by('-id').first().id
        self.assertRaises(ObjectDoesNotExist, SearchPollService().search_by_id, last_id+1)
        self.assertRaises(PollWithoutAlternativesException, SearchPollService().search_by_id, Poll.objects.get(title='F').id)