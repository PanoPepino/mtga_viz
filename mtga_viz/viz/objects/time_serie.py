from os import path

import numpy as np
from manim import *
from mtga_viz.viz.objects.pin import Pin
from mtga_viz.viz.utils.constants_viz import ARCH_COLORS, TEXT_SECONDARY, RUN_RESULT_COLORS
from scipy.interpolate import make_interp_spline


class Single_Time_Serie(Group):
    """
    To plot one single time series in the metagame data
    """

    def __init__(
        self,
        x_vals: list,         # time_windows (0 to 35)
        series_dict: dict,    # specific series entry
        color: str = RUN_RESULT_COLORS['1_win'],
        **kwargs,
    ):
        super().__init__(**kwargs)

        # 1. Data Prep
        label_text = series_dict.get('deck', "Unknown")
        y_vals = np.array(series_dict['share'])
        n_trophies = np.array(series_dict.get('trophy', []))

        y_max = max(y_vals) if max(y_vals) > 0 else 1
        x_max = max(x_vals)
        y_min = min(y_vals)

        # Labels for the axis (0, 12, 24 ... 72)
        x_numbers = range(0, 72, 2)
        y_numbers = [0, y_max, y_max/4]

        # 2. Coordinate System
        # We set range to 72. This is our visual "Hour" space.
        self.plane = NumberPlane(
            x_range=[0, 71, 4],
            y_range=[0, y_max+15, y_max/4],
            x_length=14,
            y_length=0.75,
            tips=False,
            faded_line_ratio=1,
            background_line_style={
                "stroke_color": TEXT_SECONDARY,
                "stroke_opacity": 0.2,
            },
            axis_config={
                "color": TEXT_SECONDARY,
                "include_ticks": False,
                "stroke_opacity": 0,
                "font_size": 6,
            },
            x_axis_config={
                "include_numbers": True,
                "numbers_to_include": x_numbers,
                "label_direction": 0.1*UR,
            },
            y_axis_config={
                "include_numbers": True,
                "numbers_to_include": y_numbers,
                "decimal_number_config": {"num_decimal_places": 0},
                "label_direction": 0.5*DOWN + 0.1*RIGHT
            },
        )
        self.plane.axes.set_z_index(10)

        # 3. Graph Plotting
        # We multiply the x_values by 2 so they spread from 0 to 72
        xs = np.linspace(min(x_vals)+0.2, max(x_vals)-0.1, 400)
        spl = make_interp_spline(x_vals, y_vals, k=0)
        ys = np.clip(spl(xs), 0, None)

        graph = self.plane.plot_line_graph(
            x_values=xs,
            y_values=ys,
            add_vertex_dots=False,
            line_color=color,
            stroke_width=1
        )

        # 4. Add Trophy icons
        get_trophy_path = path.join(path.dirname(__file__), "../assets/trophy.svg")
        self.trophy = SVGMobject(get_trophy_path).scale(0.5).set_z_index(10)
        trophy_dots = Group()
        for x, y, n in zip(x_vals, y_vals, n_trophies):
            if n > 0:
                trophy_indicator = Group(
                    Tex(str(int(n)) if n > 1 else "", font_size=6),
                    self.trophy.copy().scale(0.08)
                ).arrange(RIGHT, buff=0.01)

                # Multiply x by 2 to place the dot correctly on the 0-72 plane
                # Added small Y offset (y+0.1) so dot sits slightly above the line
                trophy_indicator.move_to(self.plane.c2p((x)+1/2 if x < x_max else x-0.25, y+7))
                trophy_dots.add(trophy_indicator)

        # 5. Decoration (Rectangle, Label, etc)
        self.frame = RoundedRectangle(
            corner_radius=0.05,
            width=self.plane.width,
            height=self.plane.height,
            color=TEXT_SECONDARY,
            stroke_width=1,
        ).move_to(self.plane.c2p(0, 0), aligned_edge=DL)

        self.tag = Pin(
            label=label_text,
            stroke_width=2,
            color_label=ARCH_COLORS,
        ).scale(0.9)

        self.total_trophies = Group(Tex(f"{n_trophies.sum()}", font_size=15, color=TEXT_SECONDARY),
                                    self.trophy.copy().scale(0.3)).arrange(RIGHT, buff=0.1)

        self.label = Tex(label_text, font_size=15)
        self.legend_pin = Group(self.label, self.tag).arrange(
            RIGHT, buff=0.1).next_to(self.frame, LEFT, buff=0.1)
        self.total_trophies.next_to(self.frame, RIGHT, buff=0.5, aligned_edge=RIGHT)

        self.add(self.plane, graph, trophy_dots, self.legend_pin, self.frame, self.total_trophies)
