from django.test import TestCase
from polls.models.model import Choice, Question, Vote

class Modeltest(TestCase): #TestCase fa riferimento al db

    def setUp(self):
        q1 = Question.objects.create(question_text='Quanti anni hai?')
        q1.save()
        c1 = Choice.objects.create(question = q1, choice_text='32')
        c1.save()
        c2 = Choice.objects.create(question = q1, choice_text='50')
        c2.save()
        v1 = Vote.objects.create(question = q1, choice = c1)
        v1.save()

    def test_question(self):
        q1 = Question.objects.get(question_text='Quanti anni hai?')
        self.assertEqual(q1.question_text,'Quanti anni hai?')
    
    def test_choice(self):
        c1 = Choice.objects.get(choice_text='32')
        self.assertEqual(c1.choice_text,'32')

    #Controllo che una opzione sia legata a una domanda
    def test_choice_fk(self):
        q1 = Question.objects.get(question_text='Quanti anni hai?')
        c1 = Choice.objects.get(question = q1, choice_text='32')
        self.assertEqual(c1.question.id, q1.id)
    
    #Controllo che due choice puntino a una stessa domanda
    def test_choice_samefk(self):
        c1 = Choice.objects.get(choice_text='50')
        c2 = Choice.objects.get(choice_text='32')
        self.assertEqual(c1.question.id, c2.question.id)

    #Controllo che il voto leghi una opzione e una domanda
    def test_vote_samefk(self):
        q1 = Question.objects.get(question_text='Quanti anni hai?')
        c1 = Choice.objects.get(choice_text='32')
        v1 = Vote.objects.get(question = q1, choice = c1)
        self.assertEqual(v1.question.id, q1.id)
        self.assertEqual(v1.choice.id, c1.id)