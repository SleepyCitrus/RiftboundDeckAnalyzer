from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path

from riftbounddeckexaminer.examiners.analyzers.analyzer_result import AnalyzerResult
from riftbounddeckexaminer.examiners.analyzers.deck_analyzer import DeckAnalyzer
from riftbounddeckexaminer.riftbound.card import Card, CardType
from riftbounddeckexaminer.riftbound.deck import Deck


@dataclass
class AveragesAnalyzer(DeckAnalyzer):
    """
    Uses a simplistic approach of total card copies / number of decks to generalize how
    good a card is. If a card is ran across more decks it MUST be good(?)
    """

    legend_name: str
    decks: list[Deck]
    excluded_cards: list[Card]

    @classmethod
    def analyzer_description(cls) -> str:
        return "Uses a simple formula of card copies / number of decks to generalize trends."

    def aggregate(self) -> AnalyzerResult:
        chosen_champs = defaultdict(int)
        main_deck: dict[CardType, dict[str, int]] = {}
        battlefields_counter = Counter()
        runes_counter = Counter()
        sideboard_counter = Counter()

        valid_decks: list[Deck] = []
        excluded_decks = 0

        for deck in self.decks:
            skip = False
            for excluded_card in self.excluded_cards:
                if (
                    excluded_card.type in deck.main_deck
                    and excluded_card.name in deck.main_deck[excluded_card.type]
                ):
                    skip = True
                    break

            if skip:
                excluded_decks += 1
                continue
            valid_decks.append(deck)

        for deck in valid_decks:
            chosen_champs[deck.chosen_champion] += 1

            for card_type, cards in deck.main_deck.items():
                if card_type not in main_deck:
                    main_deck[CardType(card_type)] = {}
                combined = Counter(main_deck[CardType(card_type)]) + Counter(cards)
                main_deck[CardType(card_type)] = dict(combined)

            battlefields_counter = battlefields_counter + Counter(deck.battlefields)
            runes_counter = runes_counter + Counter(deck.runes)
            sideboard_counter = sideboard_counter + Counter(deck.sideboard)

        # Include champion units as part of the main deck
        if CardType.UNIT not in main_deck:
            main_deck[CardType.UNIT] = {}
        champs_to_main_deck = Counter(main_deck[CardType.UNIT]) + Counter(chosen_champs)
        main_deck[CardType.UNIT] = dict(champs_to_main_deck)

        # Sort result from most copies to least
        combined_main_deck: dict[CardType, dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        for card_type, cards in main_deck.items():
            for name, copies in cards.items():
                combined_main_deck[card_type][name] = round(
                    copies / len(valid_decks), 2
                )

            combined_main_deck[card_type] = dict(
                sorted(
                    combined_main_deck[card_type].items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            )

        combined_chosen_champs = dict(
            sorted(
                {
                    k: round(v / len(valid_decks), 2) for k, v in chosen_champs.items()
                }.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
        combined_battlefields = dict(
            sorted(
                {
                    k: round(v / len(valid_decks), 2)
                    for k, v in dict(battlefields_counter).items()
                }.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
        combined_runes = dict(
            sorted(
                {
                    k: round(v / len(valid_decks), 2)
                    for k, v in dict(runes_counter).items()
                }.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
        combined_sideboard = dict(
            sorted(
                {
                    k: round(v / len(valid_decks), 2)
                    for k, v in dict(sideboard_counter).items()
                }.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

        return AnalyzerResult(
            excluded_cards=self.excluded_cards,
            excluded_decks=excluded_decks,
            combined_chosen_champs=combined_chosen_champs,
            combined_main_deck=combined_main_deck,
            combined_battlefields=combined_battlefields,
            combined_runes=combined_runes,
            combined_sideboards=combined_sideboard,
        )

    def output_to_json(self, results: AnalyzerResult) -> str:
        results.pretty_print()

        file_friendly_legend_name = (
            self.legend_name.replace(",", "").replace(" ", "-").lower()
        )

        output_path = Path(
            f"{Path.cwd()}/src/riftbounddeckexaminer/data/analyzer/{file_friendly_legend_name}.json"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(
                asdict(results),
                f,
                indent=4,
                default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o),
            )
            return output_path.as_posix()
