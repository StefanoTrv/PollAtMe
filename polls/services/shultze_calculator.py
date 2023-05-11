from polls.models.preference import ShultzePreference, ShultzeOpinionJudgement, Poll
from collections import defaultdict

def calculate_sequences_from_db(poll: Poll) -> dict[tuple, int]:
    preferences = ShultzePreference.objects.filter(poll=poll)
    sequences: dict[tuple, int] = defaultdict(lambda: 0)

    for preference in preferences:
        sequence = preference.get_sequence()
        sequences[sequence] += 1
    
    return dict(sequences)