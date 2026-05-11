from dataclasses import dataclass

from riftbounddeckexaminer.examiners.analyzers.analyzer_result import AnalyzerResult
from riftbounddeckexaminer.riftbound.card import Card
from riftbounddeckexaminer.riftbound.deck import Deck


@dataclass
class DeckAnalyzer:

    legend_name: str
    decks: list[Deck]
    excluded_cards: list[Card]

    def aggregate(self) -> AnalyzerResult:
        # Default
        return AnalyzerResult()

    def output_to_json(self, results: AnalyzerResult) -> str:
        # Default
        ...

    @classmethod
    def analyzer_description(cls) -> str:
        # Default
        return ""
