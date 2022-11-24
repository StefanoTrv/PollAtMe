from unittest import TestCase
from polls.services.giudizio_maggioritario import Grade
from polls.services.giudizio_maggioritario import VoteTuple
from polls.services.giudizio_maggioritario import GiudizioMaggioritario

class GiudizioMaggioritarioTest(TestCase):

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

    #test della classe VoteTuple
    def test_tuple_ordering(self):

        #creiamo un po'di tuple, per esempio quelle nell'esempio del prof
        tuple_one = VoteTuple(1, 25, Grade(4, True), 12) #voto (25, MB+, 12)

        ##test che gli attributi funzionino correttamente
        self.assertEqual(tuple_one.choice_id(),1)
        self.assertEqual(tuple_one.giuduzi_migliori(),25)
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

        listaTuple = [tuple_one, tuple_two, tuple_three]
        listaTuple.sort(reverse=True)

        self.assertEqual(listaTuple[0], tuple_two)
        self.assertEqual(listaTuple[1], tuple_three)
        self.assertEqual(listaTuple[2], tuple_one)