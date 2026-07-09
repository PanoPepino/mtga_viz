from pathlib import Path
from manim import *

from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.utils.load import load_data_plot
from mtga_viz.viz.utils.constants_viz import BG_COLOR, TEXT_PRIMARY, ARCH_COLORS, TEXT_SECONDARY
from mtga_viz.viz.objects.deck_histo import DeckShareHistogram
from mtga_viz.viz.plots.template import *


class DeckShareScene(Scene):
    DATA_DIR = None
    SOURCE = None

    def construct(self):
        self.camera.background_color = BG_COLOR

        data = load_data_plot(self.DATA_DIR)

        plot_dict = data['decks']
        general_data_dict = data['general']

        title = Tex(
            f"Deck Share (Top {plot_dict['top_n']})",
            color=TEXT_PRIMARY,
            font_size=45,
        ).to_edge(UL)

        hist = DeckShareHistogram(
            plot_dict=plot_dict,
            colors_dict=ARCH_COLORS,
            bar_height=0.4
        ).scale(0.85).next_to(title, DOWN, aligned_edge=LEFT, buff=0.5)

        info = InfoBox(
            source=f"{self.SOURCE}",
            start_date=general_data_dict["start_date"],
            end_date=general_data_dict["end_date"],
            samples=plot_dict["total"],
            font_size=15,
            comment='\\# of Decks'
        ).next_to(title, RIGHT)
        notes = Tex("$ ^{*}$ Remaining $\\%$ belongs to rogue-like decks",
                    font_size=10, color=TEXT_SECONDARY).to_corner(DR,  buff=0.2)

        self.add(title, hist, info, notes)
