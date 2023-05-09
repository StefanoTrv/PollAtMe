from django.test import TestCase
from polls.services.giudizio_maggioritario import Grade
from polls.services.giudizio_maggioritario import VoteTuple
from polls.services.giudizio_maggioritario import GiudizioMaggioritario
from polls.services.giudizio_maggioritario import GiudizioMaggioritarioPoll
from polls.services.giudizio_maggioritario import produce_vote_tuple_list

class GiudizioMaggioritarioTest(TestCase):

    fixtures: list[str] = ['test_giudizio_maggioritario.json']

    #test della classe grade
    def test_grade_ordering(self):
        #creiamo un po'di grade
        grade_one = Grade(3, True) #voto 3+
        grade_two = Grade(3, False) #voto 3-
        grade_three = Grade(2, True) #voto 2+
        
        ##testiamo le combinazioni: stando ai requisiti dovremmo avere: 1<2, 2<3, 1<3 e 1=1 2=2 3=3, dove se a < b allora a batte b

        self.assertLess(grade_one,grade_two)
        self.assertLess(grade_two,grade_three)
        self.assertGreater(grade_three,grade_one)

        self.assertEqual(grade_one,grade_one)
        self.assertEqual(grade_two,grade_two)
        self.assertEqual(grade_three,grade_three)

        self.assertNotEqual(grade_one,grade_two)

    #test della classe grade
    def test_grade_as_string(self):
        #creiamo un po'di grade
        grade_one = Grade(3, True) #voto 3+
        grade_two = Grade(3, False) #voto 3-
        grade_three = Grade(2, True) #voto 2+

        self.assertEqual('SUFFICIENTE +', str(grade_one))
        self.assertEqual('SUFFICIENTE -', str(grade_two))
        self.assertEqual('SCARSO +', str(grade_three))

    #test della classe VoteTuple
    def test_tuple_ordering(self):

        #creiamo un po'di tuple, per esempio quelle nell'esempio del prof
        tuple_one = VoteTuple(1, 25, Grade(4, True), 12) #voto (25, MB+, 12)

        ##test che gli attributi funzionino correttamente
        self.assertEqual(tuple_one.choice_id(),1)
        self.assertEqual(tuple_one.giudizi_migliori(),25)
        self.assertEqual(tuple_one.grade(), Grade(4, True))
        self.assertEqual(tuple_one.giudizi_peggiori(),12)

        #test corretto ordinamento
        
        tuple_two = VoteTuple(2, 30, Grade(3, True), 1) #voto (30, B+, 11)
        self.assertGreater(tuple_one,tuple_two)

        tuple_one = VoteTuple(1, 12, Grade(3, True), 4) #voto (12, B+, 4)
        tuple_two = VoteTuple(2, 3, Grade(3, False), 6) #voto (3, B-, 6)
        self.assertGreater(tuple_one,tuple_two)

        tuple_one = VoteTuple(1, 8, Grade(2, True), 3) #voto (8, P+, 3)
        tuple_two = VoteTuple(2, 4, Grade(2, True), 1) #voto (4, P+, 1)
        self.assertGreater(tuple_one,tuple_two)

        tuple_one = VoteTuple(1, 2, Grade(3, False), 8) #voto (2, B-, 8)
        tuple_two = VoteTuple(2, 3, Grade(3, False), 9) #voto (3, B-, 9)
        self.assertGreater(tuple_one,tuple_two)

        #test ordinamento lista di tuple
        tuple_one = VoteTuple(1, 43, Grade(3, True), 40) #voto (43, B+, 40)
        tuple_two = VoteTuple(2, 25, Grade(4, False), 45) #voto (25, MB-, 45)
        tuple_three = VoteTuple(3, 27, Grade(4, False), 48) #voto (27, MB-, 48)

        lista_tuple = [tuple_one, tuple_two, tuple_three]
        lista_tuple.sort(reverse=True)

        self.assertEqual(lista_tuple[0], tuple_two)
        self.assertEqual(lista_tuple[1], tuple_three)
        self.assertEqual(lista_tuple[2], tuple_one)

    def test_tuple_generation(self):

        #costruiamo la lista in input
        lista_voti = []
        #1
        choice_id = 1
        voti = [5]*33+[4]*10+[3]*17+[2]*10+[1]*12
        lista_voti.append({'choice_id':choice_id, 'voti':voti})

        choice_id = 2
        voti = [5]*25+[4]*30+[3]*10+[2]*10+[1]*15
        lista_voti.append({'choice_id':choice_id, 'voti':voti})

        choice_id = 3
        voti = [5]*27+[4]*25+[3]*5+[2]*6+[1]*10
        lista_voti.append({'choice_id':choice_id, 'voti':voti})

        lista_tuple = produce_vote_tuple_list(lista_voti)
        lista_tuple.sort(reverse = True)

        #l'ordine risultante dovrebbe essere 3>2>1

        tuple_one =  VoteTuple(1, 33, Grade(4, False), 39)
        self.assertEqual(lista_tuple[2], tuple_one)
        tuple_three =  VoteTuple(3, 27, Grade(4, True), 21)
        self.assertEqual(lista_tuple[0], tuple_three)
        tuple_two =  VoteTuple(2, 25, Grade(4, False), 35)
        self.assertEqual(lista_tuple[1], tuple_two)

    def test_tuple_as_string(self):
        #creiamo un po'di grade
        tuple_one = VoteTuple(1, 25, Grade(4, True), 12) #voto (25, MB+, 12)
        self.assertEqual('(25, BUONO +, 12)', str(tuple_one))


    def test_calculation_from_database(self):
        giudizio_maggioritario = GiudizioMaggioritarioPoll(1)
        winner = giudizio_maggioritario.get_winner_tuple()
        expected_winner = VoteTuple(3, 2, Grade(3, True), 1)
        self.assertEqual(winner, expected_winner)

    def test_classifica(self):
        #la classifica per il poll 1 dovrebbe essere {'C' : 1, 'B' : 3 'A' : 2}
        giudizio_maggioritario = GiudizioMaggioritarioPoll(1)
        classifica = giudizio_maggioritario.get_classifica()

        #dobbiamo verificare che le tuple siano corrette
        A_tuple = VoteTuple(1, 1, Grade(3, False), 1)
        B_tuple = VoteTuple(2, 2, Grade(2, True), 0)
        C_tuple = VoteTuple(3, 2, Grade(3, True), 1)

        expected_classifica = [{'alternative' : 'C', 'place' : 1, 'judgment' : C_tuple},{'alternative' : 'A', 'place' : 2, 'judgment' : A_tuple},{'alternative' : 'B', 'place' : 3, 'judgment' : B_tuple}]
        
        self.assertEqual(classifica, expected_classifica)

    ##testiamo che per il sondaggio numero 2 venga ritornata la classifica corretta anche se votata solamente da una persona
    def test_one_preference(self):
        giudizio_maggioritario = GiudizioMaggioritarioPoll(2)
        classifica = giudizio_maggioritario.get_classifica()

        expected_classifica = [{'alternative' : 'Bella', 'place' : 1, 'judgment' :  VoteTuple(4, 0, Grade(5, False), 0)}
                              ,{'alternative' : 'Meno bella', 'place' : 2, 'judgment' :  VoteTuple(5, 0, Grade(4, False), 0)}
                              ,{'alternative' : 'Ancora meno bella', 'place' : 3, 'judgment' :  VoteTuple(6, 0, Grade(3, False), 0)}
                              ,{'alternative' : 'Brutta', 'place' : 4, 'judgment' :  VoteTuple(7, 0, Grade(1, False), 0)}]
                              
        self.assertEqual(classifica, expected_classifica)

    
    ##testiamo che il risultato per il caso problematico mostrato dal prod adesso ritorni il risultato atteso
    def test_caso_problematico(self):
        prima_alternativa = {'choice_id' : 1, 'voti' : [5,4,4,4,4,4,3,3]}
        seconda_alternativa = {'choice_id' : 2, 'voti' : [5,5,4,4,4,4,3,1]}

        giudizioMaggioritario = GiudizioMaggioritario([prima_alternativa, seconda_alternativa])

        expected_classifica = [{'alternative' : 2, 'place' : 1, 'judgment' :  VoteTuple(2, 2, Grade(4, False), 2)}
                              ,{'alternative' : 1, 'place' : 2, 'judgment' :  VoteTuple(1, 1, Grade(4, False), 2)}]
        
        classifica = giudizioMaggioritario.get_classifica_id()

        self.assertEqual(classifica, expected_classifica)