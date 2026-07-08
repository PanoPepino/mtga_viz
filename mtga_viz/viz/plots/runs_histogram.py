from pathlib import Path
from manim import *

from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.utils.load import load_data_plot
from mtga_viz.viz.utils.constants_viz import BG_COLOR, TEXT_PRIMARY, ARCH_COLORS, TEXT_SECONDARY
from mtga_viz.viz.objects.run_histogram import *
from mtga_viz.viz.plots.template import *


class RunHistoScene(Scene):
    DATA_DIR = None

    def construct(self):
        self.camera.background_color = BG_COLOR

        data = load_data_plot(self.DATA_DIR)

        plot_dict = data['runs']
        general_data_dict = data['event']

        title = Tex(
            f"Run distribution (Top {plot_dict['top_n']})",
            color=TEXT_PRIMARY,
            font_size=45,
        ).to_edge(UL)

        hist = ResultHistogram(
            runs_dict=plot_dict['data'],   # runs.json
        ).move_to(ORIGIN+LEFT+0.5*DOWN)

        info = InfoBox(
            source='April Challenge',
            start_date=general_data_dict["start_date"],
            end_date=general_data_dict["end_date"],
            samples=general_data_dict["runs"],
            font_size=15,
            comment='\\# of Runs'
        ).next_to(title, RIGHT)
        notes = Tex("$\\%$ of total runs for a deck",
                    font_size=10, color=TEXT_SECONDARY).to_corner(DR,  buff=0.2)

        self.add(title, hist, info, notes)
