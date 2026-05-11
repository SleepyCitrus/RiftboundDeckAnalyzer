from riftbounddeckexaminer.riftbound.card import Card
from riftbounddeckexaminer.riftbound.deck import Deck


class DeckReader:

    def exclude_cards(self) -> dict[str, Card]:
        # Default implementation
        return {}

    def read_decks(self) -> list[Deck]:
        # Default implementation
        return []

    @classmethod
    def reader_description(cls) -> str:
        # Default
        return ""
