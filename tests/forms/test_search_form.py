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
            'range_start_a': '',
            'range_start_b': '',
            'range_end_a': '',
            'range_end_b': '',
        })

        assert_that(form.is_valid()).is_true()
    
    def test_non_valid_data(self):
        form = SearchPollForm({
            'title': '',
            'status': '',
            'type': '',
            'range_start_a': '05/01/0000',
            'range_start_b': '05/01/0000',
            'range_end_a': '05/01/0000',
            'range_end_b': '05/01/0000',
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
            'range_start_a': '05/01/2023',
            'range_start_b': '02/01/2023',
            'range_end_a': '05/01/2023',
            'range_end_b': '02/01/2023',
        })

        assert_that(form.is_valid()).is_false()
        assert_that(form.has_error('range_start_a')).is_true()
        assert_that(form.has_error('range_start_b')).is_false()
        assert_that(form.has_error('range_end_a')).is_true()
        assert_that(form.has_error('range_end_b')).is_false()
