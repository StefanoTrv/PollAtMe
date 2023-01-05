from polls.models import Poll, Alternative, Preference
from polls.models.preference import MajorityOpinionJudgement
import math
from django.db.models import QuerySet, Count
from typing import Any

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

    def __str__(self):

        vote_string =  MajorityOpinionJudgement.JudgeType(self._vote).name
        sign = '-'
        if self._positive:
            sign = '+'

        return vote_string + ' ' + sign

##rappresentazione delle tuple
class VoteTuple:
    def __init__(self, choice_id: int, giudizi_migliori: int, grade: Grade, giudizi_peggiori: int) -> None:
        self._choice_id = choice_id
        self._giudizi_migliori = giudizi_migliori
        self._grade = grade
        self._giudizi_peggiori = giudizi_peggiori

    ##properietà
    def choice_id(self) -> int:
        return self._choice_id
    
    def giudizi_migliori(self) -> int:
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
                return self.giudizi_migliori() < __o.giudizi_migliori()
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
                return self.giudizi_migliori() > __o.giudizi_migliori()
            if (not self.grade().positive()) and (not __o.grade().positive()): #true solo se entrambi -
                return self.giudizi_peggiori() < __o.giudizi_peggiori()
        if self.grade() < __o.grade():
            return True
        return False


    def __eq__(self, __o) -> bool:
        return (
            self.choice_id() == __o.choice_id() and
            self.giudizi_migliori() == __o.giudizi_migliori() and
            self.grade() == __o.grade() and
            self.giudizi_peggiori() == __o.giudizi_peggiori()
        )
    
    def __str__(self):
        return'(' + str(self._giudizi_migliori) + ', ' + str(self._grade) + ', ' + str(self._giudizi_peggiori) + ')'

    def sameScore(self, __o) -> bool:
        return (
            self.giudizi_migliori() == __o.giudizi_migliori() and
            self.grade() == __o.grade() and
            self.giudizi_peggiori() == __o.giudizi_peggiori()
        )
    
    

#classe che incapsula la logica per il calcolo del risultato del giudizio maggioritario
class GiudizioMaggioritario:

    ##istanziatore della classe 
    def __init__(self, id:int) -> None:
        self.tuple_list  = None
        self._question_id = id

    def question_id(self) -> int:
        return self._question_id
    
    ##ritorna l'id del vincitore secondo il giudizio maggioritario
    def get_winner_id(self) -> int:
        vote_tuple_list = self.__calculate_tuple_list()
        return vote_tuple_list[0].choice_id()
    
    ##ritorna la tupla del vincitore secondo il giudizio maggioritario
    def get_winner_tuple(self) -> VoteTuple:
        vote_tuple_list = self.__calculate_tuple_list()
        return vote_tuple_list[0]
    
    ##ritorna la lista ordinata secondo il giudizio maggioritario
    def get_tuple_list(self) -> list:
        vote_tuple_list = self.__calculate_tuple_list()
        return vote_tuple_list
    
    def __calculate_tuple_list(self):
        if self.tuple_list is None:  ##evitiamo di rieseguire le query!
            result_query = self.__get_result_list()
            vote_tuple_list = produce_vote_tuple_list(result_query)
            vote_tuple_list.sort(reverse = True)
            self.tuple_list = vote_tuple_list
        return self.tuple_list
    
    ##ritorna il nome dell'alternativa vincitrice
    def get_winner_name(self) -> str:
        winner = Alternative.objects.get(id = self.get_winner_id())
        return winner.text
    
    def get_classifica(self) -> list:
        
        ordered_tuple_list = self.__calculate_tuple_list()
        
        classifica = []

        place = 1
        offset = 0
        index = 0
        length = len(ordered_tuple_list)
        while index < length:
            if index != 0:
                if not ordered_tuple_list[index].sameScore(ordered_tuple_list[index-1]):
                    place += offset
                    offset = 0
            
            current_alternative_name = Alternative.objects.get(id = ordered_tuple_list[index].choice_id()).text
            classifica.append({'alternative' : current_alternative_name, 'place' : place, 'judgment' : ordered_tuple_list[index]})                 
            index += 1
            offset += 1

        return classifica    

    ##ritorna una lista di dictionary nella forma {'choice_id': id, 'voti': <1,4,2,...,4,1>
    ##voti più alti corrispondono a voti migliori!
    def __get_result_list(self) -> list:
        
        result_list = []
        #dobbiamo prendiamo tutte le alternative per la domanda corrente
        alternative_all : QuerySet[Alternative] = Alternative.objects.filter(poll = self.question_id())
        for alternative_key in alternative_all.values_list('pk', flat=True):
            #dobbiamo andare a prendere i giudizi
            giudizi = MajorityOpinionJudgement.objects.filter(alternative = alternative_key)
            #abbiamo i giudizi per questa alternativa, dobbiamo costruire la lista
            lista_giudizi = []
            for giudizio in giudizi:
                lista_giudizi.append(giudizio.grade)

            #alla lista associamo l'id dell'alternativa
            result_list.append({'choice_id': alternative_key, 'voti': lista_giudizi})

        return result_list

    #ritorna una lista di dict del tipo 
    #{'alternativa' : alternativa, 'lista_voti' : lista_voti} dove lista voti è una lista di dict della forma {'voto':voto, 'amount' : numero}
    #la lista è ordinata in ordine di posizione nella classifica
    def get_vote_list(self):

        results_list = self.__get_result_list()
        
        tuple_list = self.__calculate_tuple_list() #utilizziamo questo ordine per salvarci la lista di voti

        out_list = [None] * len(tuple_list)
        #iteriamo per ottenere il risultato desiderato
        for result in results_list:
            alternativa = Alternative.objects.get(id = result['choice_id']).text
            votes = result['voti']
            different_votes = [e.value for e in MajorityOpinionJudgement.JudgeType]
            different_votes.sort(reverse=True) #abbiamo i voti in ordine di valore

            lista_voti = {}
            #produciamo le tuple
            for i in range(0, len(different_votes), 1):
                amount = votes.count(different_votes[i])
                vote_name = MajorityOpinionJudgement.JudgeType(different_votes[i])
                vote_name = vote_name.name
                lista_voti.update({vote_name : amount})

            #salviamola nella corretta posizione della lista
            position = None
            for i in range(0,len(tuple_list), 1):
                if tuple_list[i].choice_id()== result['choice_id']:
                    position = i

            out_list[position]={'alternativa' : alternativa, 'lista_voti' : lista_voti}

        return out_list

        
##non dipende dall'istanza della classe quindi lo facciamo statico, così può essere testato
def produce_vote_tuple_list(result_query: list) -> list:
        
    result_list = []
    #data la lista con i voti per ogni scelta generiamo le tuple
    for element in result_query:
        #logica di generazione della tupla
        #calcolo del voto mediano
        #ordiniamo in ordine decrescente la lista di voti
        lista_voti = element['voti']

        tupla = None

        ##se la lista è vuota si crea una tupla nulla
        if len(lista_voti) == 0:
            tupla = VoteTuple(element['choice_id'],
                giudizi_migliori = 0,
                giudizi_peggiori = 0,
                grade=Grade(vote=1, positive=False))
        else:
            lista_voti.sort(reverse = True)
            giudizio_mediano = None

            if len(lista_voti) % 2 == 0 or len(lista_voti):
                giudizio_mediano = lista_voti[int(len(lista_voti) / 2)]
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
            tupla = VoteTuple(element['choice_id'],
                giudizi_migliori = giudizi_migliori,
                giudizi_peggiori = giudizi_peggiori,
                grade=grade)
            
        result_list.append(tupla)

    result_list.sort(reverse=True)
    return result_list


##Servizio per ottenere il risultato dei giudizi maggioritari, per coerenza con il servizio a scelta singola
class MajorityJudgementService:

    def __init__(self, poll: Poll) -> None:
        self.__poll = poll
    
    """
    Metodi per ottenere informazioni sul risultato del sondaggio a giudizio
    maggioritario ritornano sempre un dizionario della forma {'label': valore}

    La view può chiamare quelli che vuole ed aggiungerli al suo contesto
    """

    #ritorna un dict {'classifica' : classifica}, dove classifica è una lista di dict
    #{'alternative': alternativa, 'place' : posizione. 'vote' : voto}
    def get_classifica(self):
        classifica = self.__get_classifica()
        context = {'classifica' : classifica}    
        return context

    def __get_classifica(self):
        self.giudizio_maggioritario = GiudizioMaggioritario(self.__poll.id)
        classifica  = self.giudizio_maggioritario.get_classifica()            
        return classifica

    #ritorna un dict {'winners' : vincitori} dove vincitori è una lista di
    #alternative, in genere è 1 ma può essere superiore in caso di pareggio
    def get_winners(self):
        winners = self.__get_winners()
        context = {'winners' : winners} 
        return context

    def __get_winners(self):
        self.giudizio_maggioritario = GiudizioMaggioritario(self.__poll.id)
        classifica = self.__get_classifica()

        #filtriamo la classifica per prendere i vincitori
        winners = []
        for alternativa in classifica:
            if alternativa['place'] == 1:
                winners.append(alternativa['alternative'])

        return winners


    #ritorna un dict {'voti_alternativa' : voti_alternativa, 'ordered_votes' : lista_voti}, dove voti_alternativa è una lista di dict
    #{'alternativa' alternativa, 'lista_voti' : lista_voti} 
    # dove lista_voti è un dict della forma {'voto' : numero} e lista_voti è una lista ordinata dei voti possibili
    def get_voti_alternativa(self) :
        voti_alternativa = self.__get_voti_alternativa()
        ordered_votes = self.__get_all_votes()
        context = {'voti_alternativa' : voti_alternativa, 'ordered_votes' : ordered_votes} 
        return context

    def __get_voti_alternativa(self):
        self.giudizio_maggioritario = GiudizioMaggioritario(self.__poll.id)
        lista_voti = self.giudizio_maggioritario.get_vote_list()
        return lista_voti

    def __get_all_votes(self):
        self.giudizio_maggioritario = GiudizioMaggioritario(self.__poll.id)
        different_votes = [e.value for e in MajorityOpinionJudgement.JudgeType]
        different_votes.sort(reverse=True)

        ordered_votes = []
        for i in range(0, len(different_votes), 1):
            ordered_votes.append(MajorityOpinionJudgement.JudgeType(different_votes[i]).name)

        return ordered_votes

    #ritorna un dict {'numero_alternative' : numero_alternative}, dove numero_alternative è un intero
    # che indica il numero di alternative disponibili per questa domanda
    def get_numero_alternative(self) :
        alternative = Alternative.objects.filter(poll = self.__poll.id)
        context = {'numero_alternative' : len(alternative)} 
        return context

    #ritorna un dict {'numero_preferenze' : numero_preferenze}, dove numero_preferenze è un intero
    # che indica il numero di preferenze date per questa domanda
    def get_numero_numero_giudizi(self) :
        preferenze = Preference.objects.filter(poll = self.__poll.id)
        context = {'numero_preferenze' : len(preferenze)} 
        return context

