from django.test import TestCase

from polls.models.preference import ShultzePreference
from polls.services import shultze_calculator

class TestShultze(TestCase):
    """
    Testiamo il metodo Shultze riproducendo l'esempio di Wikipedia (ordine righe colonne matrici -> ABCDE):

    Tuple di voti:
    ('A','C','B','E','D'): 5
    ('A','D','E','C','B'): 5
    ('B','E','D','A','C'): 4
    ('C','A','B','E','D'): 3
    ('C','A','E','B','D'): 7
    ('C','B','A','D','E'): 2
    ('D','C','E','B','A'): 7
    ('E','B','A','D','C'): 8

    Matrice di preferenze:     Widest-paths:              Ranking:  
    [0, 20, 26, 30, 22]        [0, 28, 28, 30, 24]        ('E', 1)
    [25, 0, 16, 33, 18]        [25, 0, 28, 33, 24]        ('A', 2)
    [19, 29, 0, 17, 24]        [25, 29, 0, 29, 24]        ('C', 3)
    [15, 12, 28, 0, 14]        [25, 28, 28, 0, 24]        ('B', 4)
    [23, 27, 21, 31, 0]        [25, 28, 28, 31, 0]        ('D', 5)

    L'ordine di righe-colonne delle matrici secondo il nostro algoritmo è diverso -> ACBED:

    Matrice di preferenze:     Widest-paths:              Ranking:  
    [0, 26, 20, 22, 30]        [0, 28, 28, 24, 30]        ('E', 1)
    [19, 0, 29, 24, 17]        [25, 0, 29, 24, 29]        ('A', 2)
    [25, 16, 0, 18, 33]        [25, 28, 0, 24, 33]        ('C', 3)
    [23, 21, 27, 0, 31]        [25, 28, 28, 0, 31]        ('B', 4)
    [15, 28, 12, 14, 0]        [25, 28, 28, 24, 0]        ('D', 5)
    """

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
        sequences = shultze_calculator.build_preference_matrix(input)
        expected = [
            [0, 26, 20, 22, 30],
            [19, 0, 29, 24, 17],
            [25, 16, 0, 18, 33],
            [23, 21, 27, 0, 31],
            [15, 28, 12, 14, 0]
        ]
        self.assertEqual(sequences, expected)
    
    def test_widest_paths(self):
        input = [
            [0, 26, 20, 22, 30],
            [19, 0, 29, 24, 17],
            [25, 16, 0, 18, 33],
            [23, 21, 27, 0, 31],
            [15, 28, 12, 14, 0]
        ]
        widest_paths = shultze_calculator.widest_paths(input)
        expected = [
            [0, 28, 28, 24, 30],
            [25, 0, 29, 24, 29],
            [25, 28, 0, 24, 33],
            [25, 28, 28, 0, 31],
            [25, 28, 28, 24, 0]
        ]
        self.assertEqual(widest_paths, expected)
    
    def test_winner(self):
        input = [
            [0, 28, 28, 24, 30],
            [25, 0, 29, 24, 29],
            [25, 28, 0, 24, 33],
            [25, 28, 28, 0, 31],
            [25, 28, 28, 24, 0]
        ]
        val = shultze_calculator.calculate_rankings(input, ('A', 'C', 'B', 'E', 'D'))

        # Classifica
        expected = (('E', 1), ('A', 2), ('C', 3), ('B', 4), ('D', 5))

        self.assertEqual(val, expected)
