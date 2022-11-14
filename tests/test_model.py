from django.test import TestCase
from polls.models.model import Choice, Question, Vote

class Modeltest(TestCase):
    def setUp(self):
        question = Question.objects.create(question_text="Quanti anni hai?")
        question.save()
        choice1 = Choice.objects.create(question = question, choice_text="32")
        choice1.save()
        choice2 = Choice.objects.create(question = question, choice_text="50")
        choice2.save()

    def test_question(self):
        question = Question.objects.get(question_text="Quanti anni hai?")
        self.assertEqual(question.question_text, 'Quanti anni hai?')

    def test_choice_fk(self):
        question = Question.objects.get(question_text="Quanti anni hai?")
        choice = Choice.objects.get(question = question, choice_text="32")
        self.assertEqual(choice.question.id, question.id)
    
    def test_choice_samefk(self):
        choice1 = Choice.objects.get(choice_text="50")
        choice2 = Choice.objects.get(choice_text="32")
        self.assertEqual(choice1.question.id, choice2.question.id)