from polls.models.preference import ShultzePreference, ShultzeOpinionJudgement, Poll

def calculate_sequences_from_db(poll: Poll):
    preferences = ShultzePreference.objects.filter(poll=poll)
    sequences: dict = {}

    for preference in preferences:
        pass