from polls.models import Poll, SinglePreferencePoll, MajorityOpinionPoll, Alternative
import datetime

def add_single_preference_poll(title : str, text : str, alternatives : list, start_time : datetime.datetime, end_time : datetime.datetime) -> None:
    __add_generic_poll(SinglePreferencePoll(),title,text,alternatives,start_time,end_time)

def add_majority_judgment_poll(title : str, text : str, alternatives : list, start_time : datetime.datetime, end_time : datetime.datetime) -> None:
    __add_generic_poll(MajorityOpinionPoll(),title,text,alternatives,start_time,end_time)

def __add_generic_poll(poll : Poll, title : str, text : str, alternatives : list, start_time : datetime.datetime, end_time : datetime.datetime) -> None:
    poll.title = title[:100]
    poll.text = text
    poll.start = start_time
    poll.end = end_time
    poll.save()
    for alternative in alternatives:
        Alternative(text = alternative, poll = poll).save()