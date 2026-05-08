from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import TextIO

from riftbounddeckanalyzer.analyzers.deck_analyzer import DeckAnalyzer
from riftbounddeckanalyzer.decks.deck import DATE_FORMAT, Deck
from riftbounddeckanalyzer.readers.decklist_metadata import DecklistMetadata
from riftbounddeckanalyzer.readers.utils.util import get_user_input

DECKS_PATH = Path(f"{Path.cwd()}/src/riftbounddeckanalyzer/data/decklists")


@dataclass
class DeckReader:

    def read_raw_line(self, file: TextIO) -> str:
        try:
            return next(file).strip()
        except StopIteration:
            print("Reached the end of the file earlier than expected!")
        return ""

    def read_single_line(self, file: TextIO) -> tuple[str, int]:
        try:
            line = next(file).strip()
            return (line[2:], int(line[:1]))
        except StopIteration:
            print("Reached the end of the file earlier than expected!")
        return "", 0

    def read_block(self, file: TextIO) -> dict[str, int]:
        block = defaultdict(int)
        for l in file:
            if not l.strip():
                # empty line, end of block
                break
            line = l.strip()
            block[line[2:]] = int(line[:1])

        return block

    def compile_decks(self, deck_files: list[Path]) -> tuple[list[Deck], set[str]]:
        valid_decks: list[Deck] = []
        unique_cards = set()

        for deck_file in deck_files:

            placement = int("".join(filter(str.isdigit, deck_file.name.split(" ")[0])))

            with open(deck_file, "r") as f:
                deck = Deck(placement)
                skip = False
                for l in f:
                    line = l.strip()
                    if DecklistMetadata.DATE in line:
                        date = self.read_raw_line(f)
                        if not date:
                            # Bad file format, skip this deck
                            skip = True
                            break
                        deck.date = datetime.strptime(date, DATE_FORMAT)
                    elif DecklistMetadata.TOURNAMENT_SIZE in line:
                        tournament_size = self.read_raw_line(f)
                        if not tournament_size:
                            skip = True
                            break
                        deck.tournament_size = int(tournament_size)
                    elif DecklistMetadata.LEGEND in line:
                        legend, _ = self.read_single_line(f)
                        if not legend:
                            # Bad file format, skip this deck
                            skip = True
                            break
                        deck.legend = legend
                    elif DecklistMetadata.CHAMPION in line:
                        chosen_champ, _ = self.read_single_line(f)
                        if not chosen_champ:
                            # Bad file format, skip this deck
                            skip = True
                            break
                        deck.chosen_champion = chosen_champ
                    elif DecklistMetadata.MAIN_DECK in line:
                        cards = self.read_block(f)
                        deck.main_deck = cards
                        unique_cards.update(cards.keys())
                    elif DecklistMetadata.BATTLEFIELDS in line:
                        cards = self.read_block(f)
                        deck.battlefields = cards
                    elif DecklistMetadata.RUNES in line:
                        cards = self.read_block(f)
                        deck.runes = cards
                    elif DecklistMetadata.SIDEBOARD in line:
                        cards = self.read_block(f)
                        deck.sideboard = cards

                if not skip:
                    # Process parsed deck information
                    valid_decks.append(deck)

        return valid_decks, unique_cards

    def pick_legend(self):
        """
        Looks through src/riftbounddeckanalyzer/data to determine which legend to compile
        deck information about.
        """
        legends = {
            x.as_posix().split("/")[-1]: x for x in DECKS_PATH.iterdir() if x.is_dir()
        }

        user_input = get_user_input(
            legends, "Pick the legend to compile deck information about:"
        )
        decks = []
        legend_name = ""
        unique_cards = set()
        for _, legend_path in user_input.items():
            legend_name = _
            decks, unique_cards = self.compile_decks(list(legend_path.glob("*.txt")))

        excluded_cards = get_user_input(
            {x: x for x in unique_cards},
            "Choose any decks with the following cards to exclude (enter to continue):",
            multiselect=True,
        )

        analyzer = DeckAnalyzer(decks, list(excluded_cards.keys()))
        results = analyzer.aggregate()
        results.pretty_print()

        output_path = Path(
            f"{Path.cwd()}/src/riftbounddeckanalyzer/data/analyzer/{legend_name}.json"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(
                asdict(results),
                f,
                indent=4,
                default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o),
            )

            print(f"See full output at: {output_path.as_posix()}")


def main_function():
    DeckReader().pick_legend()


if __name__ == "__main__":
    main_function()
