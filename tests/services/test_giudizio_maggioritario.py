from django.test import TestCase
from polls.services.giudizio_maggioritario import GiudizioMaggioritario
from polls.services.giudizio_maggioritario import GiudizioMaggioritarioPoll

class GiudizioMaggioritarioTest(TestCase):

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

    
    ##testiamo che il risultato per il caso problematico mostrato dal prod adesso ritorni il risultato atteso
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