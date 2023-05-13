from polls.models.preference import ShultzePreference, Poll
from collections import defaultdict
from typing import Any


def calculate_sequences_from_db(poll: Poll) -> dict[tuple, int]:
    preferences = ShultzePreference.objects.filter(poll=poll)
    sequences: dict[tuple, int] = defaultdict(lambda: 0)

    for preference in preferences:
        sequence = preference.get_sequence()
        sequences[sequence] += 1

    return dict(sequences)

class ShultzeCalculator:
    sequence_votes: dict[tuple, int]
    pairwise_preferences: list[list[int]]
    strongest_paths_matrix: list[list[int]]
    rankings: list[tuple]

    candidates: tuple

    def __init__(self, orders: dict[tuple, int]):
        self.sequence_votes = orders
        self.candidates = list(orders.keys())[0]

        self.__dim = len(self.candidates)
        self.pairwise_preferences = [
            [0 for _ in range(self.__dim)] for _ in range(self.__dim)]
        self.strongest_paths_matrix = [
            [0 for _ in range(self.__dim)] for _ in range(self.__dim)]

        self.rankings = []
        for c in self.candidates:
            self.rankings.append((c, 1))

    def calculate(self):
        self.__build_preference_matrix()
        self.__widest_paths()
        self.__calculate_rankings()

    def __build_preference_matrix(self):
        all_sequences = list(self.sequence_votes.keys())

        for row in range(self.__dim):
            for col in range(self.__dim):
                if row != col:
                    for seq in all_sequences:
                        if self.__precedes(seq, self.candidates[row], self.candidates[col]):
                            self.pairwise_preferences[row][col] += self.sequence_votes[seq]

    def __precedes(self, seq: tuple, fst: Any, snd: Any) -> bool:
        return seq.index(fst) < seq.index(snd)

    def __widest_paths(self):
        for i in range(self.__dim):
            for j in range(self.__dim):
                if i != j:
                    if self.pairwise_preferences[i][j] > self.pairwise_preferences[j][i]:
                        self.strongest_paths_matrix[i][j] = self.pairwise_preferences[i][j]
                    else:
                        self.strongest_paths_matrix[i][j] = 0

        for i in range(self.__dim):
            for j in range(self.__dim):
                if i != j:
                    for k in range(self.__dim):
                        if i != k and j != k:
                            self.strongest_paths_matrix[j][k] = max(self.strongest_paths_matrix[j][k], min(
                                self.strongest_paths_matrix[j][i], self.strongest_paths_matrix[i][k]))

    def __calculate_rankings(self):
        for i in range(self.__dim):
            for j in range(self.__dim):
                if i != j:
                    if self.strongest_paths_matrix[i][j] < self.strongest_paths_matrix[j][i]:
                        self.rankings[i] = (self.rankings[i][0], self.rankings[i][1] + 1)

        self.rankings.sort(key=lambda x: x[1])
    
    def get_summary(self) -> dict[Any, list[int]]:
        """
        return a dictionary where for each candidate return the number of times it was ordered in every position
        """
        summary: dict = defaultdict(lambda: [0 for _ in range(self.__dim)])

        for seq, votes in self.sequence_votes.items():
            for i, candidate in enumerate(seq):
                summary[candidate][i] += votes

        return dict(summary)

    def get_summary_transposed(self) -> list[dict[Any, int]]:
        """
        return a list of dictionaries where for each position return the number of times each candidate was ordered in that position
        """
        summary: list[dict[Any, int]] = [defaultdict(lambda: 0) for _ in range(self.__dim)]

        for seq, votes in self.sequence_votes.items():
            for i, candidate in enumerate(seq):
                summary[i][candidate] += votes

        return summary
