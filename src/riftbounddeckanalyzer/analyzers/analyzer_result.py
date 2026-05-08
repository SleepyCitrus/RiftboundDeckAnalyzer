from dataclasses import dataclass
from pprint import pprint


@dataclass
class AnalyzerResult:

    excluded_cards: list[str]
    excluded_decks: int
    combined_chosen_champs: dict[str, float]
    combined_main_deck: dict[str, float]
    combined_battlefields: dict[str, float]
    combined_runes: dict[str, float]
    combined_sideboards: dict[str, float]

    def pretty_print(self):
        pprint(self.combined_chosen_champs)
        pprint(self.combined_main_deck)
        pprint(self.combined_battlefields)
        pprint(self.combined_runes)
        pprint(self.combined_sideboards)
