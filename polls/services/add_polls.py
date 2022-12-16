from polls.models import Poll, SinglePreferencePoll, MajorityOpinionPoll, Alternative

def add_single_preference_poll(title : str, text : str, alternatives : list) -> None:
    __add_generic_poll(SinglePreferencePoll(),title,text,alternatives)

def add_majority_judgment_poll(title : str, text : str, alternatives : list) -> None:
    __add_generic_poll(MajorityOpinionPoll(),title,text,alternatives)

def __add_generic_poll(poll : Poll, title : str, text : str, alternatives : list) -> None:
    poll.title = title[:100]
    poll.text = text
    poll.save()
    for alternative in alternatives:
        Alternative(text = alternative, poll = poll).save()