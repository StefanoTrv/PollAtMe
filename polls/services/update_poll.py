from polls.models import Poll, Alternative
import datetime

def update_poll(poll : Poll, title : str, text : str, alternatives : list, start_time : datetime.datetime, end_time : datetime.datetime) -> None:
    poll.title = title[:100]
    poll.text = text
    poll.start = start_time
    poll.end = end_time
    poll.save()
    for alt in poll.alternative_set.all():
        alt.delete()
    for alternative in alternatives:
        Alternative(text = alternative, poll = poll).save()