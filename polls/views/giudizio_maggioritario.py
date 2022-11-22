#prototipo classe per il giudizio maggioritario, solo a fine prototyping, probabilmente la classe non ha senso
class giudizioMaggioritario: 
    ##istanziatore della classe 
    def __init__(self, id:int) -> None:
        self.question_id = id

    ##ritorna il vincitore del sistema a giudizio maggioritario
    def get_winner(self) -> int:
        ##prima cosa query dei voti
        voti = self.__get_voti()
        voto_max = self.__get_voto_max()
        vote_array = self.__produce_vote_array(voti, voto_max)
        vote_tuples = self.__produce_array_tuples(vote_array)
        return self.__extract_winner(vote_tuples)

    
    ##ritorna una lista di valori nel seguente formato: <{choice_id_1 : "voto",...,{choice_id_n : "voto"}, {...}, {...}>
    def __get_voti(self) -> list:
        raise NotImplementedError("yet to be implemented")
        return None

    def __get_voto_max(self) -> list:
        raise NotImplementedError("yet to be implemented")
        return None

    def __produce_voto_array(self, voti, voto_max):
        raise NotImplementedError("yet to be implemented")
        return None
    
    def __produce_array_tuples(self, vote_array):
        raise NotImplementedError("yet to be implemented")
        return None

    def __extract_winner(self, vote_tuples):
        raise NotImplementedError("yet to be implemented")
        return None

##rappresentazione delle tuple
class voteTuple:

    def __init__(self, choice_id, giuduzi_migliori, voto, giudizi_peggiori) -> None:
        self.choice_id = choice_id
        self.giudizi_migliori = giuduzi_migliori
        self.voto = voto
        self.giudizi_peggiori = giudizi_peggiori

    def __eq__(self, other:voteTuple) -> bool:
        if(self.giudizi_migliori == other.giudizi_migliori &
           self.voto == other.voto &
           self.giudizi_peggiori == other.giudizi_peggiori):
           return True
        else:
            return False

    
#classe per la rappresentazione del voto, classe contenitore
class Grade:

    def __init__(self, vote:int, positive:bool) -> None:
        self.vote = vote
        self.positive = positive

    def get_vote(self) -> int:
        return self.vote

    def is_positive(self) -> int:
        return self.positive

    def __lt__(self, other: Grade) -> bool:
        raise NotImplementedError("yet to be implemented")
        return None
    
    def __eq__(self, __o: Grade) -> bool:
        return self.get_vote == __o.get_vote & (self.is_positive == __o.is_positive)

                

