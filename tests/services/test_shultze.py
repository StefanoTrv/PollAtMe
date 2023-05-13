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

    def test_shultze_from_wikipedia_example(self):
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
        s = shultze_calculator.ShultzeCalculator(input)
        s.calculate()

        self.assertEqual(s.pairwise_preferences, [
            [0, 26, 20, 22, 30],
            [19, 0, 29, 24, 17],
            [25, 16, 0, 18, 33],
            [23, 21, 27, 0, 31],
            [15, 28, 12, 14, 0]
        ])
        self.assertEqual(s.strongest_paths_matrix, [
            [0, 28, 28, 24, 30],
            [25, 0, 29, 24, 29],
            [25, 28, 0, 24, 33],
            [25, 28, 28, 0, 31],
            [25, 28, 28, 24, 0]
        ])
        self.assertEqual(s.rankings, [('E', 1), ('A', 2), ('C', 3), ('B', 4), ('D', 5)])
    
    def test_shultze_tie(self):
        input = {
            ('A', 'B', 'C'): 1,
            ('C', 'B', 'A'): 1,
        }
        s = shultze_calculator.ShultzeCalculator(input)
        s.calculate()
        self.assertEqual(s.rankings, [('A', 1), ('B', 1), ('C', 1)])

    def test_shultze_on_numbers(self):
        input = {
            ('1', '2', '3', '4', '5', '6'): 1,
            ('5', '3', '4', '1', '2', '6'): 3,
            ('3', '5', '2', '4', '6', '1'): 10,
            ('3', '5', '2', '4', '1', '6'): 3,
        }
        s = shultze_calculator.ShultzeCalculator(input)
        s.calculate()
        self.assertEqual(s.rankings, [('3', 1), ('5', 2), ('2', 3), ('4', 4), ('6', 5), ('1', 6)])

    def test_shultze_tie_and_losers(self):
        input = {
            ('A', 'B', 'C'): 1,
            ('B', 'A', 'C'): 2,
            ('A', 'C', 'B'): 1,
        }
        s = shultze_calculator.ShultzeCalculator(input)
        s.calculate()
        self.assertEqual(s.rankings, [('A', 1), ('B', 1), ('C', 3)])

    def test_shultze_winner_and_tie(self):
        input = {
            ('A', 'B', 'C'): 1,
            ('A' ,'C', 'B'): 1,
        }
        s = shultze_calculator.ShultzeCalculator(input)
        s.calculate()
        self.assertEqual(s.rankings, [('A', 1), ('B', 2), ('C', 2)])
    
    def test_summary(self):
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

        s = shultze_calculator.ShultzeCalculator(input)

        self.assertEqual(s.get_summary(), {
            'A': [10, 10, 10, 8, 7],
            'B': [8, 10, 8, 14, 5],
            'C': [12, 12, 0, 5, 16],
            'D': [7, 5, 8, 10, 15],
            'E': [8, 8, 19, 8, 2]
        })