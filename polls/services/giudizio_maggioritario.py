from polls.models import Poll, Alternative
from polls.models.preference import MajorityOpinionJudgement, MajorityPreference
import math
from django.db.models import QuerySet

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

        vote_string =  MajorityOpinionJudgement.JudgementType(self._vote).name
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

    ##proprietà
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
    

"""
    Classe che incapsula il risultato di una scelta a giudizio maggioritario
"""
class VoteSequence:

    def __init__(self, choice_id: int, votes:list) -> None:
        self.__votes = votes
        self.__choice_id = choice_id

    def get_choice_id(self) -> int: 
        return self.__choice_id

    def get_median_grade(self) -> int:
        return self.__calculate_median_grade(self.__votes)
    
    def get_as_tuple(self):
        tupla = None

        ##se la lista è vuota si crea una tupla nulla
        if len(self.__votes) == 0:
            tupla = VoteTuple(self.__choice_id,
                giudizi_migliori = 0,
                giudizi_peggiori = 0,
                grade=Grade(vote=1, positive=False))
        else:
            self.__votes.sort(reverse = True)
            giudizio_mediano = None

            giudizio_mediano = self.__votes[int(len(self.__votes) / 2)]

                
            ##calcolo del numero di giudizi (strettamente) migliori
            giudizi_peggiori = 0
            giudizi_migliori = 0
            for voto in self.__votes: #probabilmente ottimizzabile
                if voto > giudizio_mediano:
                    giudizi_migliori += 1
                if voto < giudizio_mediano:
                    giudizi_peggiori += 1   
                
            positive = (giudizi_migliori > giudizi_peggiori)

            grade = Grade(giudizio_mediano, positive)
            tupla = VoteTuple(self.__choice_id,
                giudizi_migliori = giudizi_migliori,
                giudizi_peggiori = giudizi_peggiori,
                grade=grade)
            
            return tupla


    #get the Ith majority grade
    #  if index == 0 returnse the first majority grade
    #  if index > len(votes) raise exception
    def get_ith_median_grade(self, index) -> int:

        if index > len(self.__votes):
            raise Exception("too big index")
        
        i = 0
        temp_list = list(self.__votes)

        while i < index:
            temp_list.sort(reverse=True)
            current_median_grade = self.__calculate_median_grade(temp_list)
            temp_list.remove(current_median_grade)
            i += 1

        return self.__calculate_median_grade(temp_list)

    def __calculate_median_grade(self, votes) -> int:

        votes.sort(reverse = True)

        if(len(votes) == 0):
            raise Exception("empty vote list")

        giudizio_mediano = votes[int(len(votes) / 2)]

        return giudizio_mediano

    #Funzioni di ordinamento

    #self <= __o allora: o sono uguali o self < other
    def __le__(self, __o) -> bool:
        if self.__eq__(__o):
            return True
        return self.__lt__(__o)

    #self < __o 
    def __lt__(self, __o) -> bool:
        if self == __o:
            return False
        else:
            index = 0
            while True:

                this_grade = self.get_ith_median_grade(index)
                other_grade = __o.get_ith_median_grade(index)

                if this_grade > other_grade:
                    return False
                if this_grade < other_grade:
                    return True
                
                index += 1
    
    #self => __o allora o sono uguali o self > __o
    def __ge__(self, __o) -> bool:
        if self.__eq__(__o):
            return True
        return self.__gt__(__o)

    
    #self > __o 
    def __gt__(self, __o) -> bool:
        if self == __o:
            return False
        else:
            index = 0
            while True:

                this_grade = self.get_ith_median_grade(index)
                other_grade = __o.get_ith_median_grade(index)

                if this_grade < other_grade:
                    return False
                if this_grade > other_grade:
                    return True
                        
                index += 1
            


    def __eq__(self, __o) -> bool:
        index = 0
        try:
            while True:

                this_median = self.get_ith_median_grade(index)
                other_median = __o.get_ith_median_grade(index)

                if this_median != other_median:
                    return False
                index += 1
        except: 
            return True





class GiudizioMaggioritario:
    
    """
        L'input deve essere nella forma di una lista di dictionary
        dove ogni dictionary è nella forma:
            "choice_id" : id
            "voti" : lista_voti

        la lista dei voti deve essere una lista di interi, valori più alti
        corrispondono ad un giudizio più alto

    """
    def __init__(self, dict_voti) -> None:
        self.dict_voti = dict_voti
        self.sequence_list = None

    ##ritorna l'id del vincitore secondo il giudizio maggioritario
    def get_winner_id(self) -> int:
        vote_tuple_list = self._calculate_tuple_sequence()
        return vote_tuple_list[0].choice_id()
    
    ##ritorna la tupla del vincitore secondo il giudizio maggioritario
    def get_winner_tuple(self) -> VoteTuple:
        vote_tuple_list = self._calculate_tuple_sequence()
        return vote_tuple_list[0]
    
    ##ritorna la lista ordinata secondo il giudizio maggioritario
    def get_tuple_list(self) -> list:
        vote_tuple_list = self._calculate_tuple_sequence()
        return vote_tuple_list
    
    def _calculate_tuple_sequence(self):
        if self.sequence_list is None:  ##evitiamo di rieseguire le query!
            self.__prepare_vote_sequence_list()
            self.sequence_list.sort(reverse = True)
        return self.sequence_list

    def __prepare_vote_sequence_list(self):
        seqence_list = []
        for element in self.dict_voti:
            seqence_list.append(VoteSequence(element['choice_id'], element['voti']))

        self.sequence_list = seqence_list
        
    ##ritorna la classifica nella forma di una lista ordinata
    def get_classifica_id(self) -> list:
        
        ordered_tuple_list = self._calculate_tuple_sequence()
        
        classifica = []

        place = 1
        offset = 0
        index = 0
        length = len(ordered_tuple_list)
        while index < length:
            if index != 0:
                if not ordered_tuple_list[index] == (ordered_tuple_list[index-1]):
                    place += offset
                    offset = 0
            
            classifica.append({'alternative' : ordered_tuple_list[index].get_choice_id(), 'place' : place, 'judgment' : ordered_tuple_list[index].get_as_tuple()})                 
            index += 1
            offset += 1

        return classifica
    
    def _get_result_list(self) -> list:
        return self.dict_voti




#classe che incapsula la logica per il calcolo del risultato del giudizio maggioritario
class GiudizioMaggioritarioPoll(GiudizioMaggioritario):

    ##istanziatore della classe 
    def __init__(self, id:int, include_synthetic:bool=True) -> None:

        self._question_id = id
        self._include_synthetic=include_synthetic

        result_list = []
        #dobbiamo prendiamo tutte le alternative per la domanda corrente
        alternative_all : QuerySet[Alternative] = Alternative.objects.filter(poll = self._question_id)
        for alternative_key in alternative_all.values_list('pk', flat=True):
            #dobbiamo andare a prendere i giudizi
            giudizi = MajorityOpinionJudgement.objects.filter(alternative = alternative_key)
            if (not self._include_synthetic):
                giudizi=giudizi.filter(preference__synthetic=False)
            #abbiamo i giudizi per questa alternativa, dobbiamo costruire la lista
            lista_giudizi = []
            for giudizio in giudizi:
                lista_giudizi.append(giudizio.grade)

            #alla lista associamo l'id dell'alternativa
            result_list.append({'choice_id': alternative_key, 'voti': lista_giudizi})

        super(GiudizioMaggioritarioPoll, self).__init__(result_list)
    
    ##ritorna il nome dell'alternativa vincitrice
    def get_winner_name(self) -> str:
        winner = Alternative.objects.get(id = self.get_winner_id())
        return winner.text
    
    def get_classifica(self) -> list:
        
        classifica = super().get_classifica_id()

        index = 0
        length = len(classifica)
        while index < length:
            current_alternative_name = Alternative.objects.get(id = classifica[index]['alternative']).text
            classifica[index] = {'alternative' : current_alternative_name,
                                 'place' :  classifica[index]['place'],
                                 'judgment' : classifica[index]['judgment']}
            index += 1

        return classifica    

    

    #ritorna una lista di dict del tipo 
    #{'alternativa' : alternativa, 'lista_voti' : lista_voti} dove lista voti è una lista di dict della forma {'voto':voto, 'amount' : numero}
    #la lista è ordinata in ordine di posizione nella classifica
    def get_vote_list(self):

        results_list = super()._get_result_list()
        
        tuple_list = self._calculate_tuple_sequence() #utilizziamo questo ordine per salvarci la lista di voti

        out_list = [None] * len(tuple_list)
        #iteriamo per ottenere il risultato desiderato
        for result in results_list:
            alternativa = Alternative.objects.get(id = result['choice_id']).text
            votes = result['voti']
            different_votes = [e.value for e in MajorityOpinionJudgement.JudgementType]
            different_votes.sort(reverse=True) #abbiamo i voti in ordine di valore

            lista_voti = {}
            #produciamo le tuple
            for i in range(0, len(different_votes), 1):
                amount = votes.count(different_votes[i])
                vote_name = MajorityOpinionJudgement.JudgementType(different_votes[i])
                vote_name = vote_name.name
                lista_voti.update({vote_name : amount})

            #salviamola nella corretta posizione della lista
            position = None
            for i in range(0,len(tuple_list), 1):
                if tuple_list[i].get_choice_id() == result['choice_id']:
                    position = i

            out_list[position]={'alternativa' : alternativa, 'lista_voti' : lista_voti}

        return out_list




"""
    A partire da una dictionari del tipo
        'choice_id' : "id"
        "voti" : lista_voti
    produce le tuple

"""
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

    def __init__(self, poll: Poll, include_synthetic:bool=True) -> None:
        self.__poll = poll
        self.include_synthetic=include_synthetic
        self.giudizio_maggioritario = GiudizioMaggioritarioPoll(self.__poll.id,include_synthetic=self.include_synthetic)
    
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
        classifica  = self.giudizio_maggioritario.get_classifica()            
        return classifica

    #ritorna un dict {'winners' : vincitori} dove vincitori è una lista di
    #alternative, in genere è 1 ma può essere superiore in caso di pareggio
    def get_winners(self):
        winners = self.__get_winners()
        context = {'winners' : winners} 
        return context

    def __get_winners(self):
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
        lista_voti = self.giudizio_maggioritario.get_vote_list()
        return lista_voti

    def __get_all_votes(self):
        different_votes = [e.value for e in MajorityOpinionJudgement.JudgementType]
        different_votes.sort(reverse=True)

        ordered_votes = []
        for i in range(0, len(different_votes), 1):
            ordered_votes.append(MajorityOpinionJudgement.JudgementType(different_votes[i]).name)

        return ordered_votes

    #ritorna un dict {'numero_alternative' : numero_alternative}, dove numero_alternative è un intero
    # che indica il numero di alternative disponibili per questa domanda
    def get_numero_alternative(self) :
        alternative = Alternative.objects.filter(poll = self.__poll.id)
        context = {'numero_alternative' : len(alternative)} 
        return context

    #ritorna il numero di preferenze date per questa domanda
    def get_numero_numero_preferenze(self) :
        preferenze = MajorityPreference.objects.filter(poll = self.__poll.id)
        if(not self.include_synthetic):
            preferenze=preferenze.filter(synthetic=False)
        return len(preferenze)
