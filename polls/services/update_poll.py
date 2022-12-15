from polls.models import Poll, Alternative

def update_poll(poll : Poll, title : str, text : str, alternatives : list) -> None:
    poll.title = title[:100]
    poll.text = text
    poll.save()
    for alt in poll.alternative_set.all():
        alt.delete()
    for alternative in alternatives:
        Alternative(text = alternative, poll = poll).save()