from pathlib import Path
from manim import *

from mtga_viz.viz.objects.deck_wr_error import DeckWRErrorPlot
from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.objects.legend_confidence import Legend_Confidence
from mtga_viz.viz.utils.load import load_data_plot, load_json
from mtga_viz.viz.utils.constants_viz import BG_COLOR, TEXT_PRIMARY, ARCH_COLORS, TEXT_SECONDARY


class DeckWRErrorScene(Scene):
    DATA_DIR = None

    def construct(self):
        self.camera.background_color = BG_COLOR

        data = load_data_plot(self.DATA_DIR)

        plot_dict = data['decks']
        general_data_dict = data['general']
        wr_dict = data['wr_interval']

        title = Tex(
            f"Win Rates (Top {plot_dict['top_n']})",
            color=TEXT_PRIMARY,
            font_size=45,
        ).to_edge(UL)

        errors = DeckWRErrorPlot(
            wr_dict=wr_dict
        ).scale(0.85).to_corner(DOWN, buff=0.1)

        info = InfoBox(
            start_date=general_data_dict["start_date"],
            end_date=general_data_dict["end_date"],
            samples=wr_dict["total_matches"],
            font_size=15,
            comment='\\# of Matches'
        ).next_to(title, RIGHT, aligned_edge=DOWN)

        legend_confidence = Tex("Bars show 95\\% confidence", font_size=10,
                                color=TEXT_SECONDARY).to_corner(DR, buff=0.2)
        self.add(title, info, errors, legend_confidence)
