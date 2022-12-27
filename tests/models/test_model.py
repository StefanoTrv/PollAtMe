from datetime import timedelta
from assertpy import assert_that #type: ignore

from django.utils import timezone
from django.test import TestCase
from polls.models import Alternative, SinglePreferencePoll, SinglePreference, Poll, MajorityOpinionPoll

class Modeltest(TestCase):

    poll_title = "Età"
    poll_text = "Quanti anni hai?"

    def setUp(self):
        poll = SinglePreferencePoll(title=self.poll_title, text=self.poll_text, 
            start=timezone.now() - timedelta(weeks=1), 
            end=timezone.now() + timedelta(weeks=1))
        poll.save()
        alternative1 = Alternative(poll = poll, text = "32")
        alternative1.save()
        alternative2 = Alternative(poll = poll, text = "50")
        alternative2.save()
        preference1 = SinglePreference(poll = poll, alternative = alternative1)
        preference1.save()

    def test_poll(self):
        poll = Poll.objects.get(title=self.poll_title)
        self.assertEqual(poll.title, self.poll_title)
        self.assertEqual(poll.text, self.poll_text)

    def test_poll_is_active(self):
        poll = Poll()
        poll.start = timezone.now()
        poll.end = timezone.now() + timedelta(weeks=1)

        self.assertTrue(poll.is_active())
        self.assertFalse(poll.is_ended())
        self.assertFalse(poll.is_not_started())

    def test_poll_is_ended(self):
        poll = Poll()
        poll.start = timezone.now() - timedelta(weeks=2)
        poll.end = timezone.now() - timedelta(weeks=1)

        self.assertFalse(poll.is_active())
        self.assertTrue(poll.is_ended())
        self.assertFalse(poll.is_not_started())
    
    def test_poll_not_started(self):
        poll = Poll()
        poll.start = timezone.now() + timedelta(weeks=1)
        poll.end = timezone.now() + timedelta(weeks=2)

        self.assertFalse(poll.is_active())
        self.assertFalse(poll.is_ended())
        self.assertTrue(poll.is_not_started())

    
    def test_poll_type_preferenza_singola(self):
        poll = SinglePreferencePoll(title=self.poll_title, text=self.poll_text, 
            start=timezone.now() - timedelta(weeks=1), 
            end=timezone.now() + timedelta(weeks=1))
        poll.save()

        self.assertEqual(poll.get_type(), 'Preferenza singola')
    
    def test_poll_type_giudizio_maggioritario(self):
        poll = MajorityOpinionPoll(title=self.poll_title, text=self.poll_text, 
            start=timezone.now() - timedelta(weeks=1), 
            end=timezone.now() + timedelta(weeks=1))
        poll.save()
        
        self.assertEqual(poll.get_type(), 'Giudizio maggioritario')

    def test_choice_fk(self):
        poll = Poll.objects.get(text=self.poll_text)
        alternative = Alternative.objects.get(poll = poll, text="32")
        self.assertEqual(alternative.poll.id, poll.id)
    
    def test_choice(self):
        a1 = Alternative.objects.get(text='32')
        self.assertEqual(a1.text,'32')
    
    #Controllo che due alternative puntino a una stessa domanda
    def test_choice_samefk(self):
        a1 = Alternative.objects.get(text='50')
        a2 = Alternative.objects.get(text='32')
        self.assertEqual(a1.poll.id, a2.poll.id)

    #Controllo che il voto leghi una opzione e una domanda
    def test_vote_samefk(self):
        q1 = Poll.objects.get(title=self.poll_title)
        a1 = Alternative.objects.get(text='32')
        p1 = SinglePreference.objects.get(poll = q1, alternative = a1)
        self.assertEqual(p1.poll.id, q1.id)
        self.assertEqual(p1.alternative.id, a1.id)