from dataclasses import dataclass
from enum import StrEnum


class CardType(StrEnum):
    LEGEND = "legend"
    CHAMPION = "champion"
    UNIT = "unit"
    GEAR = "gear"
    SPELL = "spell"
    BATTLEFIELD = "battlefields"
    RUNES = "runes"
    SIDEBOARD = "sideboard"


@dataclass(eq=True, frozen=True)
class Card:

    name: str
    type: CardType
