

from manim import *
import numpy as np
from mtga_viz.viz.constants import ART_COLORS
from dataframes import summary_archetype, summary_tricks
from mtga_viz.viz.frame import FramedPlot
from mtga_viz.viz.result_histo import *
from mtga_viz.viz.scatter_wr_vs_share import *
from mtga_viz.viz.legend import Legend

from manim import *


MathTex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)
Tex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)


class Both(Scene):
    def construct(self):
        hist = ResultHistogram(
            df=summary_archetype,
            category_col="archetype",
            result_cols=("2-0", "2-1", "1-2", "0-2"),
        )

        plot = Scatter_WR(summary_archetype, margins=4, spacing=5, scale_tag=1)
        print(summary_tricks)
        print(ART_COLORS)

        tags = Legend(
            labels=summary_tricks['tricks'],
            shares_pct=summary_tricks['numbers'],
            colors_dict=ART_COLORS,
            direction="horizontal",
            show_text=True,
            item_buff=0.1,
            show_pct_symbol=False
        )

        objs = [plot, hist, tags]
        titles = ['WR vs Meta \\%', 'Match up Breakdown', 'Counting Tricks']
        [obj.scale_to_fit_width(config.frame_width) for obj in objs]

        to_display = Group(*[FramedPlot(obj, title).scale_to_fit_width(5) for obj, title in zip(objs, titles)])

        to_display[0].scale_to_fit_height(config.frame_height-1)
        right = Group(to_display[1], to_display[2]).arrange(
            DOWN).scale_to_fit_height(config.frame_height-1)
        full_display = Group(to_display[0], right).arrange(RIGHT, buff=0.2)

        self.add(full_display)
