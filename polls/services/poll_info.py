from polls.models import Poll, Alternative, Preference
from typing import Any

from polls.services.active_polls import SearchPollService

class poll_info:

    def search_by_poll_id(self, poll_id: int) -> Any:
        self.__poll = Poll.objects.get(id = poll_id)
        self.poll = SearchPollService().search_by_id(poll_id)
        return self

    """
        Ritorna un dizionario con le informazioni del sondaggio in self.polls, 
        in caso sia necessario recuperare ulteriori informazioni si possono
        aggiungere qui i metodi per recuperarli, al momentoil vocabolario ha le seguenti coppie:
            -) "poll_id"            : id
            -) "titolo_sondaggio"   : titolo
            -) "data_inizio"        : data_inizio
            -) "data_chiusura"      : data_chiusura
            -) "numero_alternative" : numero_alternative
            -) "numero_preferenze"  : numero di preferenze
    """
    def get_poll_info(self):
        out_dict = {}
        out_dict.update({"poll_id":self.__poll})
        out_dict.update({"titolo_sondaggio":self._get_poll_title()})
        out_dict.update({"data_inizio":self._get_start_date()})
        out_dict.update({"data_chiusura":self._get_end_date()})
        out_dict.update({"numero_alternative":self._get_number_alternatives()})
        out_dict.update({"numero_preferenze":self._get_number_preferences()})

        return out_dict

    def _get_poll_title(self):
        return self.poll.title

    def _get_start_date(self):
        return self.poll.start
    
    def _get_end_date(self):
        return self.poll.end
    
    def _get_number_alternatives(self):
        alternative = Alternative.objects.filter(poll = self.__poll.id)
        return len(alternative)

    def _get_number_preferences(self):
        preferenze = Preference.objects.filter(poll = self.__poll.id)
        return len(preferenze)

