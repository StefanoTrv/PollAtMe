from polls.models.preference import ShultzePreference, Poll
from collections import defaultdict
from typing import Any

def calculate_sequences_from_db(poll: Poll) -> dict[tuple, int]:
    preferences = ShultzePreference.objects.filter(poll=poll)
    sequences: dict[tuple, int] = defaultdict(lambda: 0)

    for preference in preferences:
        sequence = preference.get_sequence()
        sequences[sequence] += 1
    
    return dict(sequences)

def calculate_rankings(p_mat: list[list], candidates: tuple) -> tuple:
    """Calculates the rankings of the candidates based on the preference matrix.

    Args:
        p_mat (list[list]): The preference matrix.

    Returns:
        tuple[tuple]: The rankings of the candidates.
    """

    n = len(p_mat)
    assert n == len(candidates)

    rankings = []

    for c in candidates:
        rankings.append((c, 1))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                if p_mat[i][j] < p_mat[j][i]:
                    rankings[i] = (rankings[i][0], rankings[i][1] + 1)
    
    rankings.sort(key=lambda x: x[1])

    return tuple(rankings)

# returns True if in given key the item in position fst precedes the item in position snd, False otherwise
def precedes(alph: dict, key: tuple, fst: int, snd: int) -> bool:
    n = len(key)
    for el1 in range(n-1):
        if list(alph.keys())[list(alph.values()).index(fst)] == key[el1]:
            for el2 in range(el1 + 1, n):
                if list(alph.keys())[list(alph.values()).index(snd)] == key[el2]:
                    return True
            return False
    return False
    
# builds a dictionary by linking items of a given tuple and an incremental counter
def alphabet(tuple: tuple) -> dict[Any, int]:
    alph = {}
    ctr = 0
    for el in tuple:
        alph[el] = ctr
        ctr += 1
    return alph
    
def build_preference_matrix(sequences: dict[tuple, int]) -> list[list[int]]:
    keys = list(sequences.keys())
    dim = len(keys[0])
    alph = alphabet(keys[0])
    mat = [[0 for i in range(dim)] for j in range(dim)]
    for row in range(dim):
        for col in range(dim):
            if row != col:
                for key in keys:
                    if precedes(alph, key, row, col):
                        mat[row][col] += sequences[key]
    return mat
