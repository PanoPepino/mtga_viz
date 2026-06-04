from manim import *
import numpy as np

from mtga_viz.viz.pin import Pin
from mtga_viz.viz.constants import ARCH_COLORS, RESULT_COLORS


class Scatter_WR(Group):
    def __init__(
        self,
        df,
        x_col: str = "share_pct",
        y_col: str = "wr",
        label_col: str = "archetype",
        margins: float = 5,
        spacing: float = 10,
        color_map=None,
        scale_tag: float = 1.3,
        ** kwargs,
    ):
        super().__init__(**kwargs)

        color_map = color_map or ARCH_COLORS

        x_min = df[x_col].min() - margins
        x_max = df[x_col].max() + margins
        y_min = df[y_col].min() - margins
        y_max = df[y_col].max() + margins

        self.axes = NumberPlane(
            x_range=[x_min, x_max, spacing],
            y_range=[y_min, y_max, spacing],
            x_length=10,
            y_length=8,
            tips=False,
            background_line_style={
                "stroke_color": BLUE,
                "stroke_opacity": 0.2,
            },
            axis_config={
                "color": GREY,
                "include_ticks": False,
                "include_numbers": True,
            },
            x_axis_config={
                "include_numbers": True,
                "numbers_to_include": np.arange(df[x_col].min(), df[x_col].max(), spacing-1),
                "label_direction": UP,
            },
            y_axis_config={
                "include_numbers": True,
                "numbers_to_include": np.arange(df[y_col].min(), df[y_col].max(), 2*spacing),
            },
        )

        labels = self.axes.get_axis_labels(
            x_label=MathTex("Presence\\, (\\%)", color=WHITE, font_size=28),
            y_label=MathTex("WR\\,(\\%)", color=WHITE, font_size=28),
        )
        labels[0].next_to(self.axes.x_axis.get_end(), UP, aligned_edge=RIGHT, buff=0.2)
        labels[-1].next_to(self.axes.y_axis.get_end(), RIGHT, aligned_edge=LEFT, buff=0.2)

        dots = Group()
        for _, row in df.iterrows():
            tag = Pin(
                label=row[label_col],
                stroke_width=2,
                color_label=color_map[row[label_col]],
            ).scale(scale_tag)
            tag.move_to(self.axes.c2p(row[x_col], row[y_col]))
            dots.add(tag)

        line_50 = DashedLine(
            self.axes.c2p(x_min, 50),
            self.axes.c2p(x_max, 50),
            color=RESULT_COLORS['2-0'],
            dash_length=0.2,
            dashed_ratio=0.8,
            stroke_width=1
        )

        self.axes = self.axes
        self.labels = labels
        self.line_50 = line_50
        self.dots = dots

        self.add(self.axes, labels, line_50, dots)
