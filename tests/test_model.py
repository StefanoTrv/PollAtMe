from django.test import TestCase
from polls.models.model import Choice, Poll, Vote

class Modeltest(TestCase):

    poll_text = "Quanti anni hai?"

    def setUp(self):
        poll = Poll(text=self.poll_text)
        poll.save()
        choice1 = Choice(poll = poll, choice_text = "32")
        choice1.save()
        choice2 = Choice(poll = poll, choice_text = "50")
        choice2.save()
        vote1 = Vote(poll = poll, choice = choice1)
        vote1.save()

    def test_poll(self):
        poll = Poll.objects.get(text=self.poll_text)
        self.assertEqual(poll.text, self.poll_text)

    def test_choice_fk(self):
        poll = Poll.objects.get(text=self.poll_text)
        choice = Choice.objects.get(poll = poll, choice_text="32")
        self.assertEqual(choice.poll.id, poll.id)
    
    def test_choice(self):
        c1 = Choice.objects.get(choice_text='32')
        self.assertEqual(c1.choice_text,'32')
    
    #Controllo che due choice puntino a una stessa domanda
    def test_choice_samefk(self):
        c1 = Choice.objects.get(choice_text='50')
        c2 = Choice.objects.get(choice_text='32')
        self.assertEqual(c1.poll.id, c2.poll.id)

    #Controllo che il voto leghi una opzione e una domanda
    def test_vote_samefk(self):
        q1 = Poll.objects.get(text=self.poll_text)
        c1 = Choice.objects.get(choice_text='32')
        v1 = Vote.objects.get(poll = q1, choice = c1)
        self.assertEqual(v1.poll.id, q1.id)
        self.assertEqual(v1.choice.id, c1.id)