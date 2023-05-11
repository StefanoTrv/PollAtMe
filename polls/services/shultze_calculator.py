from polls.models.preference import ShultzePreference, ShultzeOpinionJudgement, Poll
from collections import defaultdict

def calculate_sequences_from_db(poll: Poll) -> dict[tuple, int]:
    preferences = ShultzePreference.objects.filter(poll=poll)
    sequences: dict[tuple, int] = defaultdict(lambda: 0)

    for preference in preferences:
        sequence = preference.get_sequence()
        sequences[sequence] += 1
    
    return dict(sequences)

def calculate_rankings(p_mat: list[list], ) -> tuple:
    """Calculates the rankings of the candidates based on the preference matrix.

    Args:
        p_mat (list[list]): The preference matrix.

    Returns:
        tuple[tuple]: The rankings of the candidates.
    """

    n = len(p_mat)
    rankings = []

    for i in range(n):
        rankings.append((i, 1))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                if p_mat[i][j] < p_mat[j][i]:
                    rankings[i] = (rankings[i][0], rankings[i][1] + 1)
    
    rankings.sort(key=lambda x: x[1])

    return tuple(rankings)