from django.test import TestCase
from polls.forms import SearchPollForm
from polls.models import Alternative
from assertpy import assert_that # type: ignore

class TestSearchForm(TestCase):

    def test_empty_data(self):
        form = SearchPollForm({
            'title': '',
            'status': '',
            'type': '',
            'range_start_a_day': '',
            'range_start_a_month': '',
            'range_start_a_year': '',
            'range_start_b_day': '',
            'range_start_b_month': '',
            'range_start_b_year': '',
            'range_end_a_day': '',
            'range_end_a_month': '',
            'range_end_a_year': '',
            'range_end_b_day': '',
            'range_end_b_month': '',
            'range_end_b_year': '',
        })

        assert_that(form.is_valid()).is_true()
    
    def test_non_valid_data(self):
        form = SearchPollForm({
            'title': '',
            'status': '',
            'type': '',
            'range_start_a_day': '1',
            'range_start_a_month': '',
            'range_start_a_year': '',
            'range_start_b_day': '1',
            'range_start_b_month': '',
            'range_start_b_year': '',
            'range_end_a_day': '1',
            'range_end_a_month': '',
            'range_end_a_year': '',
            'range_end_b_day': '1',
            'range_end_b_month': '',
            'range_end_b_year': '',
        })

        assert_that(form.is_valid()).is_false()
        assert_that(form.has_error('range_start_a')).is_true()
        assert_that(form.has_error('range_start_b')).is_true()
        assert_that(form.has_error('range_end_a')).is_true()
        assert_that(form.has_error('range_end_b')).is_true()
    
    def test_wrong_range(self):
        form = SearchPollForm({           
            'title': '',
            'status': '',
            'type': '',
            'range_start_a_day': '31',
            'range_start_a_month': '12',
            'range_start_a_year': '2022',
            'range_start_b_day': '1',
            'range_start_b_month': '1',
            'range_start_b_year': '2022',
            'range_end_a_day': '31',
            'range_end_a_month': '12',
            'range_end_a_year': '2022',
            'range_end_b_day': '1',
            'range_end_b_month': '1',
            'range_end_b_year': '2022',
        })

        assert_that(form.is_valid()).is_false()
        assert_that(form.has_error('range_start_a')).is_true()
        assert_that(form.has_error('range_start_b')).is_false()
        assert_that(form.has_error('range_end_a')).is_true()
        assert_that(form.has_error('range_end_b')).is_false()
