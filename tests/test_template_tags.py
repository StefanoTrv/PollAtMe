from polls.templatetags import shuffle
from django.test import TestCase
from assertpy import assert_that  # type: ignore
import random

class ShuffleTestCase(TestCase):
    def test_shuffle_true(self):
        # probabilità che il test generi falsi positivi/falsi negativi: 1/10!
        l = random.sample(range(100), 10)
        assert_that(shuffle.shuffle(l, True)).is_not_equal_to(l)
    
    def test_shuffle_false(self):
        l = random.sample(range(100), 10)

        assert_that(shuffle.shuffle(l, False)).is_equal_to(l)