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
        return self.vote() < __o.vote()
    
    #self => __o allora o sono uguali o self > __o
    def __ge__(self, __o) -> bool:
        if self.__eq__(__o):
            return True
        return self.__gt__( __o)
    
    #self > __o allora o self.voto > __o.voto o self.voto == __o.voto & __o.positive & not self.positive
    def __gt__(self, __o) -> bool:
        if self.vote() == __o.vote():
            return __o.positive() and (not self.positive())
        return self.vote() > __o.vote()

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

    def __get_result_list(self) -> list:
        raise NotImplementedError("yet to be implemented")
        return None
    
    def __produce_vote_tuple_list(self, result_query: list) -> list:
        raise NotImplementedError("yet to be implemented")
        return None
