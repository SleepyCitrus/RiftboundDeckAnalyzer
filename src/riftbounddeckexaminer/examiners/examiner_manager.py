from riftbounddeckexaminer.examiners.analyzers.averages_analyzer import AveragesAnalyzer
from riftbounddeckexaminer.examiners.analyzers.deck_analyzer import DeckAnalyzer
from riftbounddeckexaminer.examiners.analyzers.placement_analyzer import (
    PlacementAnalyzer,
)
from riftbounddeckexaminer.examiners.readers.deck_reader import DeckReader
from riftbounddeckexaminer.examiners.readers.riftdecks_deck_reader import (
    RiftdecksDeckReader,
)
from riftbounddeckexaminer.examiners.readers.terminal_deck_reader import (
    TerminalDeckReader,
)
from riftbounddeckexaminer.utils.util import get_user_input, unpack_single_dict_entry


class ExaminerManager:

    READERS: list[DeckReader] = [TerminalDeckReader(), RiftdecksDeckReader()]
    ANALYZERS_LIST: list[type[DeckAnalyzer]] = [PlacementAnalyzer, AveragesAnalyzer]

    def examine(self):
        # Reader
        reader_options: dict[str, DeckReader] = {}
        for reader in self.READERS:
            reader_description = (
                f"{reader.__class__.__name__}: {reader.reader_description()}"
            )
            reader_options[reader_description] = reader

        _, selected_reader = unpack_single_dict_entry(
            get_user_input(options=reader_options, prompt="Select reader to use:")
        )

        decks = selected_reader.read_decks()
        print(f"Found {len(decks)} decks!")

        excluded_cards = selected_reader.exclude_cards()

        # Analyzer
        analyzer_options: dict[str, type[DeckAnalyzer]] = {}
        for analyzer in self.ANALYZERS_LIST:
            anaylzer_description = (
                f"{analyzer.__name__}: {analyzer.analyzer_description()}"
            )
            analyzer_options[anaylzer_description] = analyzer
        _, selected_analyzer = unpack_single_dict_entry(
            get_user_input(options=analyzer_options, prompt="Select analyzer to use:")
        )

        if decks:
            legend_name = decks[0].legend
            analyzer = selected_analyzer(
                legend_name=legend_name,
                decks=decks,
                excluded_cards=[x for _, x in excluded_cards.items()],
            )

            results = analyzer.aggregate()
            print("Analysis complete!")

            print("Printing deck analysis results:")
            output_path = analyzer.output_to_json(results)
            print(f"See full output at: {output_path}")


def main_function():
    ExaminerManager().examine()


if __name__ == "__main__":
    main_function()
