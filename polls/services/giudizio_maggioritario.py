from polls.models import Poll, Alternative
from polls.models.preference import MajorityOpinionJudgement, MajorityPreference
from django.db.models import QuerySet
        
"""
    A class that encapsulates the judgments obtained through majority judgment for an alternative. 
"""
class AlternativeJudgments:

    """
        Constructor:
        @param choice_id: an int that identifies the sequence
        @param votes: list of votes, the bigger the vote the better the judgement
    """
    def __init__(self, choice_id: int, votes:list) -> None:
        self.__votes = votes
        self.__choice_id = choice_id
        self.__medians: list = []

    """
        Returns the id of the alternative
    """
    def get_choice_id(self) -> int: 
        return self.__choice_id

    """
        Returns the median grade of the set of the alternatives
    """
    def get_median_grade(self) -> int:
        return self.__calculate_median_grade(self.__votes)

    """
        get the Ith majority grade
          if index == 0 returns the first majority grade
          if index > len(votes) raise exception
    """
    def get_ith_median_grade(self, index) -> int:

        if index > len(self.__votes):
            raise Exception("too big index")
        
        if index < len(self.__medians):
            return self.__medians[index]

        i = 0
        temp_list = list(self.__votes)

        while i < index:
            temp_list.sort(reverse=True)
            current_median_grade = self.__calculate_median_grade(temp_list)

            if i == len(self.__medians):
                self.__medians.append(current_median_grade)

            temp_list.remove(current_median_grade)
            i += 1

        return self.__calculate_median_grade(temp_list)

    def __calculate_median_grade(self, votes) -> int:

        votes.sort(reverse = True)

        if(len(votes) == 0):
            raise Exception("empty vote list")

        giudizio_mediano = votes[int(len(votes) / 2)]

        return giudizio_mediano

    '''
        Ordering functions, allow comparation between vote sequences
    '''

    #self <= __o allora: are equal or self < other
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
    
    #self => __o are equal or o self > __o
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



'''
    Class that incapsulates the Majority Judgment results calculation.
    Allow comparation between arbitrary alternatives and do not depend on the dadabase.
'''
class GiudizioMaggioritario:
    
    """
        Constructor:
        @param dict_voti: a list representing the votes.

        Input has to be a list of dictionaries, with each one in the form:
            "choice_id" : id
            "voti" : lista_voti
        Where choice_id is an integer that idendifies the alternative and
        lista_voti is the list of votes.
        Each vote must be an integer, a bigger integer is a better vote.

    """
    def __init__(self, dict_voti) -> None:
        self.dict_voti = dict_voti
        self.sequence_list = None

    """
        Returns the id of the winner, calculated using the majority judgement
        algorithm
    """
    def get_winner_id(self) -> int:
        vote_tuple_list = self._calculate_tuple_sequence()
        return vote_tuple_list[0].choice_id()
    
    """
        Returns a list ordered from the winner to the loser
    """
    def get_tuple_list(self) -> list:
        vote_tuple_list = self._calculate_tuple_sequence()
        return vote_tuple_list
    
    def _calculate_tuple_sequence(self):
        if self.sequence_list is None:
            self.__prepare_vote_sequence_list()
            self.sequence_list.sort(reverse = True)
        return self.sequence_list

    def __prepare_vote_sequence_list(self):
        seqence_list = []
        for element in self.dict_voti:
            seqence_list.append(AlternativeJudgments(element['choice_id'], element['voti']))

        self.sequence_list = seqence_list
        
    """
        Returns the results as a list of couples alternative-id - place.
        The results is in the form of a list of dictionaries, where each dictionary is in the form:
            'alternative' : value   ##alternative id
            'place' : value         ##place in the standings
    """
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
            
            classifica.append({'alternative' : ordered_tuple_list[index].get_choice_id(), 'place' : place})                 
            index += 1
            offset += 1

        return classifica
    
    def _get_result_list(self) -> list:
        return self.dict_voti



'''
    Class that incapsulates the Majority Judgment results calculation for
    a specific poll in the database.
'''
class GiudizioMaggioritarioPoll(GiudizioMaggioritario):

    """
        Constructor:
        @param id: the id of the poll to calculate the results of
        @param include_syntetic: if true it will use syntetic_votes.
    """
    def __init__(self, id:int, include_synthetic:bool=True) -> None:

        self._question_id = id
        self._include_synthetic=include_synthetic

        result_list = []
        #getting the alternatives for the current question
        alternative_all : QuerySet[Alternative] = Alternative.objects.filter(poll = self._question_id)
        for alternative_key in alternative_all.values_list('pk', flat=True):
            #getting the judgements for a specific alternative
            giudizi = MajorityOpinionJudgement.objects.filter(alternative = alternative_key)
            if (not self._include_synthetic):
                giudizi=giudizi.filter(preference__synthetic=False)
            #constructing the list
            lista_giudizi = []
            for giudizio in giudizi:
                lista_giudizi.append(giudizio.grade)

            #associating the list to the id of the alternative
            result_list.append({'choice_id': alternative_key, 'voti': lista_giudizi})

        super(GiudizioMaggioritarioPoll, self).__init__(result_list)
    
    """
        Returns the name of the alternative
    """
    def get_winner_name(self) -> str:
        winner = Alternative.objects.get(id = self.get_winner_id())
        return winner.text
    
    """
        Returns the result, it differs from the parent class result because it uses the
        alternatives name instead of the ids
    """
    def get_classifica(self) -> list:
        
        classifica = super().get_classifica_id()

        index = 0
        length = len(classifica)
        while index < length:
            current_alternative_name = Alternative.objects.get(id = classifica[index]['alternative']).text
            classifica[index] = {'alternative' : current_alternative_name,
                                 'place' :  classifica[index]['place']}
            index += 1

        return classifica    
    

    """
       Returns a list of dictionaries in the form:
            'alternativa' : alternativa   ##alternative's name
            'lista_voti' : lista_voti
        Where lista_voti is a list of dictionaries in the form:
            'voto' : amount
        i.e. "buono" : 10

        Useful to see the number of specific judgements an alternative has received
    """
    def get_vote_list(self):

        results_list = super()._get_result_list()
        
        tuple_list = self._calculate_tuple_sequence() #using the order to save the list of votes

        out_list = [None] * len(tuple_list)

        for result in results_list:
            alternativa = Alternative.objects.get(id = result['choice_id']).text
            votes = result['voti']
            different_votes = [e.value for e in MajorityOpinionJudgement.JudgementType]
            different_votes.sort(reverse=True)

            lista_voti = {}
            
            for i in range(0, len(different_votes), 1):
                amount = votes.count(different_votes[i])
                vote_name = MajorityOpinionJudgement.JudgementType(different_votes[i])
                vote_name = vote_name.name
                lista_voti.update({vote_name : amount})

            #saving in the correct position of the list
            position = None
            for i in range(0,len(tuple_list), 1):
                if tuple_list[i].get_choice_id() == result['choice_id']:
                    position = i

            out_list[position]={'alternativa' : alternativa, 'lista_voti' : lista_voti}

        return out_list


"""
    Class that incapsulates the service for accessing the results of a majority judgement poll
"""
class MajorityJudgementService:


    """
        Constructor:
        @param poll: the poll to calculate the results of
        @param include_syntetic: if true it will use syntetic_votes.

    """

    def __init__(self, poll: Poll, include_synthetic:bool=True) -> None:
        self.__poll = poll
        self.include_synthetic=include_synthetic
        self.giudizio_maggioritario = GiudizioMaggioritarioPoll(self.__poll.id,include_synthetic=self.include_synthetic)

    """
        Returns a dictionary in the form:
            'classifica' : classifica
        Where classifica is a list of dict in the form:
            'alternative' : value   ##alternative's name
            'place' : value         ##place in the standings
    """
    def get_classifica(self):
        classifica = self.__get_classifica()
        context = {'classifica' : classifica}    
        return context

    def __get_classifica(self):
        classifica  = self.giudizio_maggioritario.get_classifica()            
        return classifica

    """
        Returns a dictionary in the form:
            'winners' : winners
        Where winners is a list of the winners's names
    """
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

    """
        Returns a dict of the form:
            'voti_alternativa' : voti_alternativa
            'ordered_votes' : lista_voti
        Where voti alternativa is a list of dictionaries in the form:
            'alternativa' : alternativa
            'lista_voti' : lista_voti
        Where lista_voti is a list of dictionaries in the form:
            'voto' : amount
        ordered_votes is the ordered list of the passible judgements
    """
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

    """
        Returns a dict of the form:
            'numero_alternative' : numero_alternative
        Where numero_alternative is the number of the possible alternatives for this poll
    """
    def get_numero_alternative(self) :
        alternative = Alternative.objects.filter(poll = self.__poll.id)
        context = {'numero_alternative' : len(alternative)} 
        return context

    """
        Returns the number of preferences for this poll
    """
    def get_numero_numero_preferenze(self) :
        preferenze = MajorityPreference.objects.filter(poll = self.__poll.id)
        if(not self.include_synthetic):
            preferenze=preferenze.filter(synthetic=False)
        return len(preferenze)