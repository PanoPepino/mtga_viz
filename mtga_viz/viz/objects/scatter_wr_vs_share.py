from manim import *
import numpy as np
import math


from mtga_viz.viz.objects.pin import Pin
from mtga_viz.viz.utils.constants_viz import ARCH_COLORS, RESULT_COLORS, TEXT_SECONDARY


class Scatter_WR(Group):
    def __init__(
        self,
        share_plot_dict,
        wr_plot_dict,
        spacing_x: float = 3,
        spacing_y: float = 3,
        color_map=None,
        scale_tag: float = 1,
        x_length: float = 9,
        y_length: float = 6,
        frame_radius: float = 0.1,
        **kwargs,
    ):
        super().__init__(**kwargs)

        color_map = color_map or ARCH_COLORS

        share_map = dict(zip(share_plot_dict["labels"], share_plot_dict["shares_pct"]))
        wr_map = dict(zip(wr_plot_dict["labels"], wr_plot_dict["wr"]))

        labels = [lab for lab in share_plot_dict["labels"] if lab in wr_map]

        x_vals = [share_map[lab] for lab in labels]
        y_vals = [wr_map[lab] for lab in labels]

        x_min = min(x_vals) - 2
        x_max = max(x_vals) + 2
        y_min = min(y_vals) - 2
        y_max = max(y_vals) + 2

        x_numbers = np.arange(x_min+2, x_max, spacing_x)
        y_numbers = np.arange(y_min+2, y_max, spacing_y)

        self.plane = NumberPlane(
            x_range=[x_min, x_max, spacing_x],
            y_range=[y_min, y_max, spacing_y],
            x_length=x_length,
            y_length=y_length,
            tips=False,
            faded_line_ratio=1,
            background_line_style={
                "stroke_color": TEXT_SECONDARY,
                "stroke_opacity": 0.2,
            },
            axis_config={
                "color": TEXT_SECONDARY,
                "include_ticks": False,
                "include_numbers": True,
                "stroke_opacity": 0,
                "font_size": 15
            },
            x_axis_config={
                "include_numbers": True,
                "numbers_to_include": x_numbers,
                "label_direction": UP,
            },
            y_axis_config={
                "include_numbers": True,
                "numbers_to_include": y_numbers,
            },
        )

        axis_labels = self.plane.get_axis_labels(
            x_label=MathTex("Presence\\,(\\%)", color=WHITE, font_size=25),
            y_label=MathTex("WR\\,(\\%)", color=WHITE, font_size=25),
        )
        axis_labels[0].next_to(self.plane.x_axis.get_end(), DOWN, aligned_edge=RIGHT, buff=0.2)
        axis_labels[1].next_to(self.plane.y_axis.get_end(), UP, aligned_edge=LEFT, buff=0.2)

        dots = Group()
        for lab in labels:
            tag = Pin(
                label=lab,
                stroke_width=2,
                color_label=color_map,
            ).scale(scale_tag)
            tag.move_to(self.plane.c2p(share_map[lab], wr_map[lab]))
            dots.add(tag)

        line_50 = DashedLine(
            self.plane.c2p(x_min, 50),
            self.plane.c2p(x_max, 50),
            color=RESULT_COLORS["2-0"],
            dash_length=0.2,
            dashed_ratio=0.8,
            stroke_width=1,
        )

        self.frame = RoundedRectangle(
            corner_radius=frame_radius,
            width=self.plane.width,
            height=self.plane.height,
            color=TEXT_SECONDARY,
            stroke_width=2,
        ).move_to(self.plane.c2p(x_min, y_min), aligned_edge=DL)

        self.axis_labels = axis_labels
        self.line_50 = line_50
        self.dots = dots

        self.add(self.plane, axis_labels, self.frame, line_50, dots)
