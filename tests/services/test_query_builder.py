from django.test import TestCase
from polls.models import Poll
from django.utils import timezone
from datetime import timedelta
from polls.services import SearchPollQueryBuilder
from assertpy import assert_that # type: ignore

class TestQueryBuilder(TestCase):

    def setUp(self) -> None:
        self.titles = ['Lorem ipsum', 'dolor sit amet', 'consectetur adipiscing', 'Lorem ipsum dolor sit amet', 'enim eget consectetur', 'sapien tellus tristique lorem']
        self.texts = ['Lorem ipsum', 'dolor sit amet', 'consectetur adipiscing', 'Nulla pulvinar', 'enim eget consectetur', 'sapien tellus tristique lorem']
        self.starts = [
            timezone.now() - timedelta(days=1),
            timezone.now() - timedelta(days=1),
            timezone.now() - timedelta(weeks=1),
            timezone.now() - timedelta(weeks=1),
            timezone.now() - timedelta(weeks=2),
            timezone.now() - timedelta(weeks=2)
        ]
        self.ends = [
            timezone.now() + timedelta(weeks=1),
            timezone.now() + timedelta(weeks=1),
            timezone.now() + timedelta(weeks=2),
            timezone.now() + timedelta(weeks=2),
            timezone.now() + timedelta(weeks=4),
            timezone.now() + timedelta(weeks=4)
        ]

        for title, text, start, end in zip(self.titles, self.texts, self.starts, self.ends):
            Poll.objects.create(title=title, text=text, start=start, end=end)
    
    def test_empty_query(self):
        query = SearchPollQueryBuilder().search()
        all_polls = Poll.objects.all()
        for poll in query:
            assert_that(all_polls).contains(poll)
    
    def test_title(self):
        query = SearchPollQueryBuilder().title_filter("L").search()
        expected_polls = Poll.objects.filter(title__startswith="L")
        for poll in query:
            assert_that(expected_polls).contains(poll)

    def test_status_filter(self):
        query = SearchPollQueryBuilder().status_filter('NOT_STARTED').search()
        active_polls = Poll.objects.filter(id__in = [
            poll.id for poll in Poll.objects.all() if poll.is_not_started()
        ])
        for poll in query:
            assert_that(active_polls).contains(poll)
        
        query = SearchPollQueryBuilder().status_filter('ACTIVE').search()
        active_polls = Poll.objects.filter(id__in = [
            poll.id for poll in Poll.objects.all() if poll.is_active()
        ])
        for poll in query:
            assert_that(active_polls).contains(poll)
        
        query = SearchPollQueryBuilder().status_filter('ENDED').search()
        active_polls = Poll.objects.filter(id__in = [
            poll.id for poll in Poll.objects.all() if poll.is_ended()
        ])
        for poll in query:
            assert_that(active_polls).contains(poll)
    
    def test_type(self):
        """
        Reimplementare modello prima
        """

    def test_range_start(self):
        start = timezone.now()
        query = SearchPollQueryBuilder().start_range_filter(start=start).search()
        expected_polls = Poll.objects.filter(start__gte=start)
        for poll in query:
            assert_that(expected_polls).contains(poll)
        
        end = timezone.now()
        query = SearchPollQueryBuilder().start_range_filter(end=end).search()
        expected_polls = Poll.objects.filter(start__lte=end)
        for poll in query:
            assert_that(expected_polls).contains(poll)

    def test_range_end(self):
        start = timezone.now()
        query = SearchPollQueryBuilder().end_range_filter(start=start).search()
        expected_polls = Poll.objects.filter(end__gte=start)
        for poll in query:
            assert_that(expected_polls).contains(poll)
        
        end = timezone.now()
        query = SearchPollQueryBuilder().end_range_filter(end=end).search()
        expected_polls = Poll.objects.filter(end__lte=end)
        for poll in query:
            assert_that(expected_polls).contains(poll)
    
    def test_complex(self):
        query = SearchPollQueryBuilder().title_filter("Lorem").status_filter("NOT_STARTED").search()
        expected_polls = Poll.objects.filter(id__in = [
            poll.id
            for poll in Poll.objects.all() if poll.is_not_started() and poll.title.startswith("Lorem")
        ])
        for poll in query:
            assert_that(expected_polls).contains(poll)