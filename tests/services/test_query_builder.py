from django.test import TestCase
from polls.models import Poll
from django.utils import timezone
from datetime import timedelta
from polls.services import SearchPollQueryBuilder
from assertpy import assert_that # type: ignore
from django.db.models import Q

class TestQueryBuilder(TestCase):
    def setUp(self) -> None:
        polls = [
            {'title': 'A', 'text': 'A', 'default_type': 1, 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1)},  # concluso   
            {'title': 'B', 'text': 'B', 'default_type': 3, 'start': timezone.now() - timedelta(weeks=2), 'end': timezone.now() - timedelta(weeks=1)},  # concluso
            {'title': 'C', 'text': 'C', 'default_type': 2, 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2)},  # attivo
            {'title': 'D', 'text': 'D', 'default_type': 1, 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2)},  # attivo
            {'title': 'E', 'text': 'E', 'default_type': 3, 'start': timezone.now() + timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2)},  # non ancora attivo
            {'title': 'F', 'text': 'F', 'default_type': 2, 'start': timezone.now(), 'end': timezone.now()},  # senza opzioni
        ]

        for p_dict in polls:
            p = Poll(**p_dict)
            p.save()
        
        for poll in Poll.objects.filter(~Q(title='F')):
            poll.alternative_set.create(text="Prova1")
            poll.alternative_set.create(text="Prova2")

    
    def test_empty_query(self):
        query = SearchPollQueryBuilder().search()
        all_polls = [p for p in Poll.objects.all() if p.alternative_set.count() > 0]
        assert_that(all_polls).is_equal_to(query)
        
    
    def test_title(self):
        query = SearchPollQueryBuilder().title_filter("A").search()
        expected_polls = [p for p in Poll.objects.filter(title__icontains="A") if p.alternative_set.count() > 0]
        assert_that(expected_polls).is_equal_to(query)

    def test_status_filter(self):
        query = SearchPollQueryBuilder().status_filter('NOT_STARTED').search()
        expected_polls = [p for p in Poll.objects.filter(id__in = [
            poll.id for poll in Poll.objects.all() if poll.is_not_started()
        ]) if p.alternative_set.count() > 0 ]
        assert_that(expected_polls).is_equal_to(query)
        
        query = SearchPollQueryBuilder().status_filter('ACTIVE').search()
        expected_polls = [p for p in Poll.objects.filter(id__in = [
            poll.id for poll in Poll.objects.all() if poll.is_active()
        ]) if p.alternative_set.count() > 0 ]
        assert_that(expected_polls).is_equal_to(query)
        
        query = SearchPollQueryBuilder().status_filter('ENDED').search()
        expected_polls = [p for p in Poll.objects.filter(id__in = [
            poll.id for poll in Poll.objects.all() if poll.is_ended()
        ]) if p.alternative_set.count() > 0 ]
        assert_that(expected_polls).is_equal_to(query)
    
    def test_type(self):
        query = SearchPollQueryBuilder().type_filter(Poll.PollType.MAJORITY_JUDGMENT).search()
        expected_polls = [p for p in Poll.objects.filter(default_type=Poll.PollType.MAJORITY_JUDGMENT)]
        assert_that(expected_polls).is_equal_to(query)

    def test_range_start(self):
        start = timezone.now()
        query = SearchPollQueryBuilder().start_range_filter(start=start).search()
        expected_polls = [p for p in Poll.objects.filter(start__gte=start) if p.alternative_set.count() > 0]
        assert_that(expected_polls).is_equal_to(query)
        
        end = timezone.now()
        query = SearchPollQueryBuilder().start_range_filter(end=end).search()
        expected_polls = [p for p in Poll.objects.filter(start__lte=end) if p.alternative_set.count() > 0]
        assert_that(expected_polls).is_equal_to(query)

    def test_range_end(self):
        start = timezone.now()
        query = SearchPollQueryBuilder().end_range_filter(start=start).search()
        expected_polls = [p for p in Poll.objects.filter(end__gte=start) if p.alternative_set.count() > 0]
        assert_that(expected_polls).is_equal_to(query)
        
        end = timezone.now()
        query = SearchPollQueryBuilder().end_range_filter(end=end).search()
        expected_polls = [p for p in Poll.objects.filter(end__lte=end) if p.alternative_set.count() > 0]
        assert_that(expected_polls).is_equal_to(query)
    
    def test_complex(self):
        query = SearchPollQueryBuilder().title_filter("B").status_filter("NOT_STARTED").search()
        expected_polls = [p for p in Poll.objects.filter(id__in = [
            poll.id
            for poll in Poll.objects.all() if poll.is_not_started() and poll.title.startswith("B")
        ]) if p.alternative_set.count() > 0]
        assert_that(expected_polls).is_equal_to(query)