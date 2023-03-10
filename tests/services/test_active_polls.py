from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.test import TestCase
from django.utils import timezone

from polls.exceptions import PollWithoutAlternativesException
from polls.models import Poll
from polls.services import PollsListService, SearchPollService
from polls.forms.search_poll_form import SearchPollForm


class TestActivePollsService(TestCase):
    
    def setUp(self) -> None:
        self.u = User.objects.create_user(username='test')
        polls = [
            {'title': 'A', 'text': 'A', 'start': timezone.now() - timedelta(weeks=3), 'end': timezone.now() - timedelta(weeks=2), 'author': self.u, 'visibility': Poll.PollVisibility.PUBLIC},  # concluso pubblico
            {'title': 'B', 'text': 'B', 'start': timezone.now() - timedelta(weeks=3), 'end': timezone.now() - timedelta(weeks=1), 'author': self.u, 'visibility': Poll.PollVisibility.PUBLIC},  # concluso pubblico
            {'title': 'C', 'text': 'C', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': self.u, 'visibility': Poll.PollVisibility.PUBLIC},  # attivo pubblico
            {'title': 'D', 'text': 'D', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=1), 'author': self.u, 'visibility': Poll.PollVisibility.PUBLIC},  # attivo pubblico
            {'title': 'E', 'text': 'E', 'start': timezone.now() + timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': self.u, 'visibility': Poll.PollVisibility.PUBLIC},  # non ancora attivo pubblico
            {'title': 'F', 'text': 'F', 'start': timezone.now(), 'end': timezone.now(), 'author': self.u},  # senza opzioni
            {'title': 'G', 'text': 'G', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': self.u},  # attivo nascosto
            {'title': 'H', 'text': 'H', 'start': timezone.now() - timedelta(weeks=3), 'end': timezone.now() - timedelta(weeks=1), 'author': self.u},  # concluso nascosto
        ]

        for p_dict in polls:
            Poll.objects.create(**p_dict)
        
        for poll in Poll.objects.filter(~Q(title='F')):
            poll.alternative_set.create(text="Prova1")
            poll.alternative_set.create(text="Prova2")


    def test_costruzione_sondaggi_pubblici(self):
        queryset = PollsListService().get_ordered_queryset()
        excluded = Poll.objects.filter(Q(title__in = ['E', 'F']))
        for poll in excluded:
            assert_that(queryset).does_not_contain(poll)


    def test_costruzione_sondaggi_personali(self):
        queryset = PollsListService().get_my_polls(author = self.u)
        excluded = Poll.objects.filter(Q(title__in = ['F']))
        should_contain = Poll.objects.filter(Q(title__in = ['E']))
        for poll in excluded:
            assert_that(queryset).does_not_contain(poll)
        for poll in should_contain:
            assert_that(queryset).contains(poll)


    def test_sondaggi_ordine_crescente(self):
        queryset = PollsListService().get_ordered_queryset()
        
        # Mostra prima i sondaggi attivi
        assert_that(queryset).is_sorted(lambda x: x.is_active(), reverse=True)

        assert_that([poll for poll in queryset if poll.is_active()]).is_sorted(lambda x: x.end)
        assert_that([poll for poll in queryset if poll.is_ended()]).is_sorted(lambda x: x.end, reverse=True)
        
    
    def test_sondaggi_ordine_decrescente(self):
        queryset = PollsListService().get_ordered_queryset(desc=True)
        
        # Mostra prima i sondaggi attivi
        assert_that(queryset).is_sorted(lambda x: x.is_active(), reverse=True)
        assert_that([poll for poll in queryset if poll.is_active()]).is_sorted(lambda x: x.end, reverse=True)
        assert_that([poll for poll in queryset if not poll.is_active()]).is_sorted(lambda x: x.end)
    
    def test_filtro_nascosti_sondaggi_pubblici(self):

        ##filtro attivo
        queryset = PollsListService().get_ordered_queryset(desc=True)

        included = Poll.objects.filter(Q(title__in = ['A', 'B', 'C', 'D']))
        excluded = Poll.objects.filter(Q(title__in = ['E', 'F', 'G', 'H']))

        for poll in excluded:
            assert_that(queryset).does_not_contain(poll)
        for poll in included:
            assert_that(queryset).contains(poll)

        ##filtro disattivo

        queryset = PollsListService().get_ordered_queryset(desc=True, include_hidden=True)

        included = Poll.objects.filter(Q(title__in = ['A', 'B', 'C', 'D', 'G', 'H']))
        excluded = Poll.objects.filter(Q(title__in = ['E', 'F']))

        for poll in excluded:
            assert_that(queryset).does_not_contain(poll)
        for poll in included:
            assert_that(queryset).contains(poll)




    """
    def test_order_by_text(self):
        queryset = PollsListService().get_ordered_queryset(by_field='text')
        assert_that(queryset).is_sorted(lambda x: x.is_active(), reverse=True)
        assert_that([poll for poll in queryset if poll.is_active()]).is_sorted(lambda x: x.text)
        assert_that([poll for poll in queryset if not poll.is_active()]).is_sorted(lambda x: x.text)
    """

class TestSearchPollService(TestCase):
    
    def setUp(self) -> None:
        u = User.objects.create_user(username='test')
        polls = [
            {'title': 'A', 'text': 'A', 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1), 'author': u, 'visibility': Poll.PollVisibility.PUBLIC},  # concluso pubblico  
            {'title': 'B', 'text': 'B', 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1), 'author': u, 'visibility': Poll.PollVisibility.PUBLIC},  # concluso pubblico
            {'title': 'C', 'text': 'C', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': u, 'visibility': Poll.PollVisibility.PUBLIC},  # attivo pubblico
            {'title': 'D', 'text': 'D', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': u, 'visibility': Poll.PollVisibility.PUBLIC},  # attivo pubblico
            {'title': 'E', 'text': 'E', 'start': timezone.now() + timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': u, 'visibility': Poll.PollVisibility.PUBLIC},  # non ancora attivo pubblico
            {'title': 'F', 'text': 'F', 'start': timezone.now(), 'end': timezone.now(), 'author': u},  # senza opzioni
            {'title': 'G', 'text': 'G', 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1), 'author': u},  # concluso privato  
            {'title': 'H', 'text': 'H', 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1), 'author': u},  # concluso privato
            {'title': 'I', 'text': 'I', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': u},  # attivo privato
            {'title': 'J', 'text': 'J', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': u},  # attivo privato
            {'title': 'K', 'text': 'K', 'start': timezone.now() + timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': u},  # non ancora attivo privato

        ]

        for p_dict in polls:
            p = Poll(**p_dict)
            p.save()
        
        for poll in Poll.objects.filter(~Q(title='F')):
            poll.alternative_set.create(text="Prova1")
            poll.alternative_set.create(text="Prova2")

    def test_search_by_id(self):
        expected_poll = Poll.objects.get(title='A')
        poll = SearchPollService().search_by_id(expected_poll.id)
        assert_that(poll).is_equal_to(expected_poll)
        assert_that(poll.alternative_set).is_equal_to(expected_poll.alternative_set)
    
    def test_search_by_error(self):
        last_id = Poll.objects.all().order_by('-id').first().id
        self.assertRaises(Http404, SearchPollService().search_by_id, last_id+1)
        self.assertRaises(PollWithoutAlternativesException, SearchPollService().search_by_id, Poll.objects.get(title='F').id)

    def test_exclude_hidden(self):
        
        data = {'Titolo': ''}
        
        standard_poll_form = SearchPollForm(data = data)

        assert_that(standard_poll_form.is_valid()).is_true()

        queryset = standard_poll_form.to_query().search()
        expected_poll = Poll.objects.get(title='A')
        poll = SearchPollService().search_by_id(expected_poll.id)
        assert_that(poll).is_equal_to(expected_poll)
        assert_that(poll.alternative_set).is_equal_to(expected_poll.alternative_set)

        included = Poll.objects.filter(Q(title__in = ['A', 'B', 'C', 'D', 'E']))
        excluded = Poll.objects.filter(Q(title__in = ['F', 'G', 'H', 'I', 'J', 'K']))

        for poll in excluded:
            assert_that(queryset).does_not_contain(poll)
        for poll in included:
            assert_that(queryset).contains(poll)