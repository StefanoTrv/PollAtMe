from polls.models import Poll, Alternative, SinglePreference
from polls.models.preference import MajorityOpinionJudgement
import math
from django.db.models import QuerySet, Count

#classe per la rappresentazione del voto, classe contenitore
#voto maggiore => giudizio peggiore
class Grade:
    def __init__(self, vote:int, positive:bool) -> None:
        self._vote = vote
        self._positive = positive

    #più basso è il voto migliore è
    def vote(self) -> int:
        return self._vote

    #se true ha il simbolo +, altrimenti -, + batte -
    def positive(self) -> bool:
        return self._positive

    ##funzioni per gestire l'ordine
    #self <= __o allora o sono uguali o self < __o
    def __le__(self, __o) -> bool:
        if self.__eq__(__o):
            return True
        return self.__lt__( __o)

    #self < __o allora o self.voto < __o.voto o self.voto == __o.voto & self.positive & not __o.positive
    def __lt__(self, __o) -> bool:
        if self.vote() == __o.vote():
            return self.positive() and (not __o.positive())
        return self.vote() > __o.vote()
    
    #self => __o allora o sono uguali o self > __o
    def __ge__(self, __o) -> bool:
        if self.__eq__(__o):
            return True
        return self.__gt__( __o)
    
    #self > __o allora o self.voto > __o.voto o self.voto == __o.voto & __o.positive & not self.positive
    def __gt__(self, __o) -> bool:
        if self.vote() == __o.vote():
            return __o.positive() and (not self.positive())
        return self.vote() < __o.vote()

    def __eq__(self, __o) -> bool:
        return (self.vote() == __o.vote()) and (self.positive() == __o.positive())

##rappresentazione delle tuple
class VoteTuple:
    def __init__(self, choice_id: int, giuduzi_migliori: int, grade: Grade, giudizi_peggiori: int) -> None:
        self._choice_id = choice_id
        self._giudizi_migliori = giuduzi_migliori
        self._grade = grade
        self._giudizi_peggiori = giudizi_peggiori

    ##properietà
    def choice_id(self) -> int:
        return self._choice_id
    
    def giuduzi_migliori(self) -> int:
        return self._giudizi_migliori
    
    def grade(self) -> Grade:
        return self._grade
    
    def giudizi_peggiori(self) -> int:
        return self._giudizi_peggiori
    
    ##funzioni di ordinamento
    #self <= __o allora: o sono uguali o self < other
    def __le__(self, __o) -> bool:
        if self.__eq__(__o):
            return True
        return self.__lt__(__o)

    #self < __o 
    def __lt__(self, __o) -> bool:
        if self.grade() == __o.grade():
            if self.grade().positive() and __o.grade().positive(): #true solo se entrambi +
                return self.giuduzi_migliori() < __o.giuduzi_migliori()
            if (not self.grade().positive()) and (not __o.grade().positive()): #true solo se entrambi -
                return self.giudizi_peggiori() > __o.giudizi_peggiori()
        if self.grade() > __o.grade():
            return True
        return False
    
    #self => __o allora o sono uguali o self > __o
    def __ge__(self, __o) -> bool:
        if self.__eq__(__o):
            return True
        return self.__gt__(__o)

    
    #self > __o 
    def __gt__(self, __o) -> bool:
        if (self.grade()) == (__o.grade()):
            if self.grade().positive() and __o.grade().positive(): #true solo se entrambi +
                return self.giuduzi_migliori() > __o.giuduzi_migliori()
            if (not self.grade().positive()) and (not __o.grade().positive()): #true solo se entrambi -
                return self.giudizi_peggiori() < __o.giudizi_peggiori()
        if self.grade() < __o.grade():
            return True
        return False


    def __eq__(self, __o) -> bool:
        return (
            self.choice_id() == __o.choice_id() and
            self.giuduzi_migliori() == __o.giuduzi_migliori() and
            self.grade() == __o.grade() and
            self.giudizi_peggiori() == __o.giudizi_peggiori()
        )
    
    

#classe che incapsula la logica per il calcolo del risultato del giudizio maggioritario
class GiudizioMaggioritario:

    ##istanziatore della classe 
    def __init__(self, id:int) -> None:
        self._question_id = id

    def question_id(self) -> int:
        return self._question_id
    
    ##ritorna l'id del vincitore secondo il giudizio maggioritario
    def get_winner(self) -> int:
        result_query = self.__get_result_list()
        vote_tuple_list = self.__produce_vote_tuple_list(result_query)
        vote_tuple_list.sort(reverse = True)
        return vote_tuple_list[0].choice_id()
    

    ##ritorna una lista di dictionary nella forma {'choice_id': id, 'voti': <1,4,2,...,4,1>
    ##voti più alti corrispondono a voti migliori!
    def __get_result_list(self) -> list:
        
        result_list = []
        #dobbiamo prendiamo tutte le alternative per la domanda corrente
        alternative : QuerySet[Alternative] = Alternative.objects.filter(poll = self.question_id())
        for alternativa in alternative:
            #dobbiamo andare a prendere i giudizi
            giudizi = MajorityOpinionJudgement.objects.filter(id = alternativa.id)
            #abbiamo i giudizi per questa alternativa, dobbiamo costruire la lista
            lista_giudizi = []
            for giudizio in giudizi:
                lista_giudizi.append(giudizio.grade)

            #alla lista associamo l'id dell'alternativa
            result_list.append({'choice_id': alternativa.id, 'voti': lista_giudizi})

        return result_list
    
    def __produce_vote_tuple_list(self, result_query: list) -> list:
        
        result_list = []
        #data la lista con i voti per ogni scelta generiamo le tuple
        for element in result_query:
            
            #logica di generazione della tupla
            #calcolo del voto mediano
            #ordiniamo in ordine decrescente la lista di voti
            lista_voti = element['voti']
            lista_voti.sort(reverse = True)
            giudizio_mediano = None
            if len(lista_voti) % 2 == 0:
                giudizio_mediano = lista_voti[len(lista_voti) / 2]
            else:
                giudizio_mediano = lista_voti[math.ceil(len(lista_voti) / 2)]
            
            ##calcolo del numero di giudizi (strettamente) migliori
            giudizi_peggiori = 0
            giudizi_migliori = 0
            for voto in lista_voti: #probabilmente ottimizzabile
                if voto > giudizio_mediano:
                    giudizi_migliori += 1
                if voto < giudizio_mediano:
                    giudizi_peggiori += 1   
            
            positive = (giudizi_migliori > giudizi_peggiori)

            grade = Grade(giudizio_mediano, positive)
            tupla = VoteTuple(lista_voti['choice_id'],
                giuduzi_migliori = giudizi_migliori,
                giudizi_peggiori = giudizi_peggiori,
                grade=grade)
            
            result_list.append(tupla)

        return result_list