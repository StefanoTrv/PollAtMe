from polls.models.preference import ShultzePreference, ShultzeOpinionJudgement, Poll
from collections import defaultdict

def calculate_sequences_from_db(poll: Poll) -> dict[tuple, int]:
    preferences = ShultzePreference.objects.filter(poll=poll)
    sequences: dict[tuple, int] = defaultdict(lambda: 0)

    for preference in preferences:
        sequence = preference.get_sequence()
        sequences[sequence] += 1
    
    return dict(sequences)

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
    
# builds a dictionary by linking items of a given list and an incremental counter
def alphabet(lst) -> dict:
    alph = {}
    ctr = 0
    for ch in lst:
        alph[ch] = ctr
        ctr += 1
    return alph
    
def build_preference_matrix(sequences):
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