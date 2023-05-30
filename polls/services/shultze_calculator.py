from polls.models.preference import ShultzePreference, Poll
from collections import defaultdict
from typing import Any


def calculate_sequences_from_db(poll: Poll) -> dict[tuple, int]:
    """
    Calculates the sequences and their vote counts for a given poll.

    Args:
        poll: The poll object.

    Returns:
        A dictionary mapping sequences to their vote counts.
    """
    preferences = ShultzePreference.objects.filter(poll=poll)
    sequences: dict[tuple, int] = defaultdict(lambda: 0)

    for preference in preferences:
        sequence = preference.get_sequence()
        sequences[sequence] += 1

    return dict(sequences)

class ShultzeCalculator:
    """
    A calculator for determining rankings using the Schulze method.
    """
    sequence_votes: dict[tuple, int]
    pairwise_preferences: list[list[int]]
    shultze_table: list[list[int]]
    rankings: list[tuple]

    candidates: tuple

    def __init__(self, orders: dict[tuple, int]):
        """
        Initializes the ShultzeCalculator.

        Args:
            orders: A dictionary mapping sequences to their vote counts.
        """
        self.sequence_votes = orders
        self.candidates = list(orders.keys())[0]

        self.__dim = len(self.candidates)
        self.pairwise_preferences = [
            [0 for _ in range(self.__dim)] for _ in range(self.__dim)]
        self.shultze_table = [
            [0 for _ in range(self.__dim)] for _ in range(self.__dim)]

        self.rankings = []
        for c in self.candidates:
            self.rankings.append((c, 1))

    def calculate(self):
        """
        Performs the Schulze calculation to determine rankings.
        """
        self.__build_preference_matrix()
        self.__widest_paths()
        self.__calculate_rankings()

    def __build_preference_matrix(self):
        """
        Builds the pairwise preference matrix based on the given sequences and vote counts.
        """
        all_sequences = list(self.sequence_votes.keys())

        for row in range(self.__dim):
            for col in range(self.__dim):
                if row != col:
                    for seq in all_sequences:
                        if self.__precedes(seq, self.candidates[row], self.candidates[col]):
                            self.pairwise_preferences[row][col] += self.sequence_votes[seq]

    def __precedes(self, seq: tuple, fst: Any, snd: Any) -> bool:
        """
        Checks if the first candidate precedes the second candidate in the given sequence.

        Args:
            seq: The sequence of candidates.
            fst: The first candidate.
            snd: The second candidate.

        Returns:
            True if the first candidate precedes the second candidate, False otherwise.
        """
        return seq.index(fst) < seq.index(snd)

    def __widest_paths(self):
        """
        Calculates the widest paths between candidates using the pairwise preference matrix.
        """
        for i in range(self.__dim):
            for j in range(self.__dim):
                if i != j:
                    if self.pairwise_preferences[i][j] > self.pairwise_preferences[j][i]:
                        self.shultze_table[i][j] = self.pairwise_preferences[i][j]
                    else:
                        self.shultze_table[i][j] = 0

        for i in range(self.__dim):
            for j in range(self.__dim):
                if i != j:
                    for k in range(self.__dim):
                        if i != k and j != k:
                            self.shultze_table[j][k] = max(self.shultze_table[j][k], min(
                                self.shultze_table[j][i], self.shultze_table[i][k]))

    def __calculate_rankings(self):
        """
        Calculates the final rankings based on the widest paths table.
        """
        for i in range(self.__dim):
            for j in range(self.__dim):
                if i != j:
                    if self.shultze_table[i][j] < self.shultze_table[j][i]:
                        self.rankings[i] = (self.rankings[i][0], self.rankings[i][1] + 1)

        self.rankings.sort(key=lambda x: x[1])
    
    def get_summary(self) -> dict[Any, list[int]]:
        """
        Returns a dictionary where each candidate is mapped to a list of the number of times it was ordered in each position.

        Returns:
            A dictionary mapping candidates to their position-wise vote counts.
        """
        summary: dict = defaultdict(lambda: [0 for _ in range(self.__dim)])

        for seq, votes in self.sequence_votes.items():
            for i, candidate in enumerate(seq):
                summary[candidate][i] += votes

        return dict(summary)

    def get_summary_transposed(self) -> list[dict[Any, int]]:
        """
        Returns a list of dictionaries where each position is mapped to the number of times each candidate was ordered in that position.

        Returns:
            A list of dictionaries mapping positions to candidate-wise vote counts.
        """
        summary: list[dict[Any, int]] = [{c: 0 for c in self.candidates} for _ in range(self.__dim)]

        for seq, votes in self.sequence_votes.items():
            for i, candidate in enumerate(seq):
                summary[i][candidate] += votes

        return summary
