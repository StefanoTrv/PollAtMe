from django.test import TestCase
from polls.models import Alternative, SinglePreferencePoll, SinglePreference, Poll, Preference

class Modeltest(TestCase):

    poll_title = "Età"
    poll_text = "Quanti anni hai?"

    def setUp(self):
        poll = SinglePreferencePoll(title=self.poll_title, text=self.poll_text)
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