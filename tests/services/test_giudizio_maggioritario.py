from django.test import TestCase
from polls.services.giudizio_maggioritario import GiudizioMaggioritario, AlternativeJudgments
from polls.services.giudizio_maggioritario import GiudizioMaggioritarioPoll

# test della classe che calcola i risultati delle nostre scelte (quindi dal database) in giudizio maggioritario
class TestGiudizioMaggioritarioPoll(TestCase):

    fixtures: list[str] = ['test_giudizio_maggioritario.json']

    def test_classifica(self):
        #la classifica per il poll 1 dovrebbe essere {'C' : 1, 'B' : 3 'A' : 2}
        giudizio_maggioritario = GiudizioMaggioritarioPoll(1)
        classifica = giudizio_maggioritario.get_classifica()

        expected_classifica = [{'alternative' : 'C', 'place' : 1},{'alternative' : 'A', 'place' : 2},{'alternative' : 'B', 'place' : 3}]
        
        self.assertEqual(classifica, expected_classifica)

    ##testiamo che per il sondaggio numero 2 venga ritornata la classifica corretta anche se votata solamente da una persona
    def test_one_preference(self):
        giudizio_maggioritario = GiudizioMaggioritarioPoll(2)
        classifica = giudizio_maggioritario.get_classifica()

        expected_classifica = [{'alternative' : 'Bella', 'place' : 1}
                              ,{'alternative' : 'Meno bella', 'place' : 2}
                              ,{'alternative' : 'Ancora meno bella', 'place' : 3}
                              ,{'alternative' : 'Brutta', 'place' : 4}]
                              
        self.assertEqual(classifica, expected_classifica)


# test delle classi che calcolando i risultati con il metodo del giudizio maggioritario
class TestGiudizioMaggioritario(TestCase):

    def test_vote_sequence(self):
        sequence = AlternativeJudgments(1, [5,4,4,4,4,4,3,3,1,1])

        ##corretto l'id
        self.assertEqual(1, sequence.get_choice_id())

        ##prima passata dei giudizi mediani
        self.assertEqual(4, sequence.get_median_grade())
        self.assertEqual(4, sequence.get_ith_median_grade(0))        
        
        self.assertEqual(3, sequence.get_ith_median_grade(2))
        self.assertEqual(4, sequence.get_ith_median_grade(3))
        
        self.assertEqual(4, sequence.get_ith_median_grade(5))
        self.assertEqual(1, sequence.get_ith_median_grade(6))
        
        self.assertEqual(1, sequence.get_ith_median_grade(8))
        self.assertEqual(5, sequence.get_ith_median_grade(9))

        self.assertRaises(Exception, sequence.get_ith_median_grade, 10)

        ##seconda passata dei giudizi mediani
        self.assertEqual(4, sequence.get_median_grade())
                
        self.assertEqual(4, sequence.get_ith_median_grade(1))
        self.assertEqual(3, sequence.get_ith_median_grade(2))
        
        self.assertEqual(3, sequence.get_ith_median_grade(4))
        self.assertEqual(4, sequence.get_ith_median_grade(5))
        
        self.assertEqual(4, sequence.get_ith_median_grade(7))
        
        self.assertEqual(5, sequence.get_ith_median_grade(9))

        self.assertRaises(Exception, sequence.get_ith_median_grade, 10)

    def test_vote_sequence_order(self):

        first_sequence = AlternativeJudgments(1, [5,4,4,4,4,3,3,1,1])
        second_sequence = AlternativeJudgments(1, [5,4,4,4,3,3,3,1,1])

        self.assertEqual(first_sequence,first_sequence)
        self.assertEqual(second_sequence,second_sequence)

        self.assertTrue(first_sequence > second_sequence)
        self.assertTrue(first_sequence >= second_sequence)
        self.assertFalse(first_sequence < second_sequence)
        self.assertFalse(first_sequence <= second_sequence)

        self.assertFalse(first_sequence > first_sequence)
        self.assertTrue(first_sequence >= first_sequence)
        self.assertFalse(first_sequence < first_sequence)
        self.assertTrue(first_sequence <= first_sequence)
    
    #testiamo che il risultato per il caso problematico mostrato dal prod adesso ritorni il risultato atteso
    # O B B B B B S S  => (1, B-, 2)
    # O O B B B B S P  => (2, B-, 2)
    # Pareggio nei negativi 
    # -> per la distribuzione dei voti ci aspettiamo vinca il secondo.
    def test_caso_problematico(self):
        prima_alternativa = {'choice_id' : 1, 'voti' : [5,4,4,4,4,4,3,3]}
        seconda_alternativa = {'choice_id' : 2, 'voti' : [5,5,4,4,4,4,3,1]}

        giudizioMaggioritario = GiudizioMaggioritario([prima_alternativa, seconda_alternativa])

        expected_classifica = [{'alternative' : 2, 'place' : 1}
                              ,{'alternative' : 1, 'place' : 2}]
        
        classifica = giudizioMaggioritario.get_classifica_id()

        self.assertEqual(classifica, expected_classifica)


    def test_pareggio(self):
        prima_alternativa =   {'choice_id' : 1, 'voti' : [5,4,4,5,4,4,3,3]}
        seconda_alternativa = {'choice_id' : 2, 'voti' : [5,5,4,4,4,4,3,3]}

        giudizioMaggioritario = GiudizioMaggioritario([prima_alternativa, seconda_alternativa])

        expected_classifica1 = [{'alternative' : 2, 'place' : 1}
                              ,{'alternative' : 1, 'place' : 1}]
        expected_classifica2 = [{'alternative' : 1, 'place' : 1}
                              ,{'alternative' : 2, 'place' : 1}]
        
        classifica = giudizioMaggioritario.get_classifica_id()

        self.assertTrue(classifica == expected_classifica1 or classifica == expected_classifica2)

    
    def test_misto_pareggio(self):
        prima_alternativa =   {'choice_id' : 1, 'voti' : [5,4,4,5,4,4,5,5]} #1
        seconda_alternativa = {'choice_id' : 2, 'voti' : [5,5,4,4,4,4,3,3]} #2
        terza_alternativa =   {'choice_id' : 3, 'voti' : [5,4,4,5,4,4,3,3]} #2
        quarta_alternativa = {'choice_id' : 4, 'voti' : [5,5,4,4,4,4,3,3]} #2
        quinta_alternativa =   {'choice_id' : 5, 'voti' : [4,4,4,3,3,2,2,2]} #5
        sesta_alternativa = {'choice_id' : 6, 'voti' : [4,4,4,3,2,2,3,2]} #5
        settima_alternativa = {'choice_id' : 7, 'voti' : [3,3,3,2,2,2,1,1]} #7

        classifica_attesa = [1,2,2,2,5,5,7]

        giudizioMaggioritario = GiudizioMaggioritario([prima_alternativa, seconda_alternativa, terza_alternativa, 
                                                       quarta_alternativa, quinta_alternativa, sesta_alternativa, 
                                                       settima_alternativa
                                                    ])
        
        classifica = giudizioMaggioritario.get_classifica_id()

        for element in classifica:
            self.assertEqual(classifica_attesa[element['alternative'] - 1], element['place'])


    def test_molti_voti_pareggio(self):
        prima_alternativa =   {'choice_id' : 1, 'voti' : [5,5,5,5,5,5,5,4,4,4,3,3,3,3,3,3,3,2,2,2]} #1
        seconda_alternativa = {'choice_id' : 2, 'voti' : [5,5,5,4,4,4,4,4,4,4,3,3,3,2,2,2,1,1,1,1]} #2
        terza_alternativa =   {'choice_id' : 3, 'voti' : [5,5,5,3,3,3,3,3,3,3,3,3,3,2,2,2,1,1,1,1]} #3
        quarta_alternativa =  {'choice_id' : 4, 'voti' : [5,5,5,5,5,5,4,4,4,3,2,2,2,2,2,2,1,1,1,1]} #5
        quinta_alternativa =  {'choice_id' : 5, 'voti' : [5,5,5,4,4,4,2,2,2,2,2,2,2,1,1,1,1,1,1,1]} #6
        sesta_alternativa =   {'choice_id' : 6, 'voti' : [5,5,5,3,3,3,3,3,3,3,3,3,3,2,2,2,1,1,1,1]} #3

        classifica_attesa = [1,2,3,5,6,3]

        giudizioMaggioritario = GiudizioMaggioritario([terza_alternativa, quinta_alternativa, seconda_alternativa, prima_alternativa, quarta_alternativa, sesta_alternativa])
            
        classifica = giudizioMaggioritario.get_classifica_id()

        for element in classifica:
            self.assertEqual(classifica_attesa[element['alternative'] - 1], element['place'])