from django.test import TestCase
from polls.models.model import Choice, Poll, Vote

class Modeltest(TestCase):

    poll_text = "Quanti anni hai?"

    def setUp(self):
        poll = Poll.objects.create(question_text=self.poll_text)
        poll.save()
        choice1 = Choice.objects.create(question = poll, choice_text="32")
        choice1.save()
        choice2 = Choice.objects.create(question = poll, choice_text="50")
        choice2.save()

    def test_question(self):
        poll = Poll.objects.get(question_text=self.poll_text)
        self.assertEqual(poll.question_text, self.poll_text)

    def test_choice_fk(self):
        poll = Poll.objects.get(question_text=self.poll_text)
        choice = Choice.objects.get(question = poll, choice_text="32")
        self.assertEqual(choice.question.id, poll.id)
    
    def test_choice_samefk(self):
        choice1 = Choice.objects.get(choice_text="50")
        choice2 = Choice.objects.get(choice_text="32")
        self.assertEqual(choice1.question.id, choice2.question.id)