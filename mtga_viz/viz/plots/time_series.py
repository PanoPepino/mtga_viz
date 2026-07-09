

import numpy as np


import numpy as np
from manim import *
from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.objects.time_serie import Single_Time_Serie
from mtga_viz.viz.utils.constants_viz import BG_COLOR, TEXT_PRIMARY
from mtga_viz.viz.utils.load import load_data_plot


class TimeSeriesScene(Scene):
    DATA_DIR = None  # Entry points from renders
    SOURCE = None

    def construct(self):
        self.camera.background_color = BG_COLOR

        data = load_data_plot(self.DATA_DIR)
        tseries = data['time_series']
        general_data_dict = data['general']
        top_n = data['runs']
        print(len(tseries['series']))

        title = Tex(
            f"Deck use Chronology (Top {top_n['top_n']})",
            color=TEXT_PRIMARY,
            font_size=40,
        ).to_edge(UL)

        graphs = Group(*[Single_Time_Serie(
            x_vals=tseries['time_windows'],
            series_dict=tseries['series'][i]) for i in range(len(tseries['series']))]).arrange(DOWN, buff=0.1, aligned_edge=RIGHT)

        info = InfoBox(
            source=f"{self.SOURCE}",
            start_date=general_data_dict["start_date"],
            end_date=general_data_dict["end_date"],
            samples=general_data_dict["runs"],
            comment='\\# of Runs',
            font_size=13
        ).next_to(title, RIGHT)

        graphs.scale_to_fit_height(config.frame_height-1.5)
        graphs.to_corner(DOWN, buff=0.3)

        self.add(graphs, title, info)
