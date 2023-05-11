from django.test import TestCase

from polls.models.preference import ShultzePreference
from polls.services import shultze_calculator

class TestShultze(TestCase):
    fixtures = ['test_shultze.json']

    def test_calculate_occurrences(self):
        p = ShultzePreference.objects.get(pk=2)
        seq_dict = shultze_calculator.calculate_sequences_from_db(p.poll)
        self.assertEqual(seq_dict, {
            (1, 2, 3, 4, 5): 2,
            (1, 2, 3, 5, 4): 1,
            (3, 5, 2, 1, 4): 1,
            (4, 2, 3, 1, 5): 1,
            (1, 2, 4, 5, 3): 1,
            (3, 2, 5, 4, 1): 1
        })

    def test_preference_matrix(self):
        input = {
            ('A', 'C', 'B', 'E', 'D'): 5,
            ('A', 'D', 'E', 'C', 'B'): 5,
            ('B', 'E', 'D', 'A', 'C'): 8,
            ('C', 'A', 'B', 'E', 'D'): 3,
            ('C', 'A', 'E', 'B', 'D'): 7,
            ('C', 'B', 'A', 'D', 'E'): 2,
            ('D', 'C', 'E', 'B', 'A'): 7,
            ('E', 'B', 'A', 'D', 'C'): 8
        }

        expected = [
            [0, 20, 26, 30, 22],
            [25, 0, 16, 33, 18],
            [19, 29, 0, 17, 24],
            [15, 12, 28, 0, 14],
            [23, 27, 21, 31, 0]
        ]
    
    def test_widest_paths(self):
        input = [
            [0, 20, 26, 30, 22],
            [25, 0, 16, 33, 18],
            [19, 29, 0, 17, 24],
            [15, 12, 28, 0, 14],
            [23, 27, 21, 31, 0]
        ]

        expected = [
            [0, 28, 28, 30, 24],
            [25, 0, 28, 33, 24],
            [25, 29, 0, 29, 24],
            [25, 28, 28, 0, 24],
            [25, 28, 28, 31, 0]
        ]
    
    def test_winner(self):
        input = [
            [0, 28, 28, 30, 24],
            [25, 0, 28, 33, 24],
            [25, 29, 0, 29, 24],
            [25, 28, 28, 0, 24],
            [25, 28, 28, 31, 0]
        ]

        # Classifica
        expected = ((4), (0), (2), (1), (3))
