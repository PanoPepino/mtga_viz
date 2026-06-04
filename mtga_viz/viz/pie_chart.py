
from manim import *


class Pie_Sectors(VGroup, Mobject):
    def __init__(
        self,
        labels: list,
        shares_rad: list,
        colors_dict: dict,
        inner_rad: float = 0,
        outer_rad: float = 2,
        opa: float = 0.6,
        stroke_color=WHITE,
        stroke_width: float = 1.5,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.sectors = VGroup()

        self.fake_circle = Circle(radius=outer_rad+0.8, stroke_opacity=0)

        angles = [float(x) for x in shares_rad]
        colors = [colors_dict[k] for k in labels]

        start = 0.0
        for ang, color, in zip(angles, colors):
            share_sector = AnnularSector(
                outer_radius=outer_rad,
                inner_radius=inner_rad,
                start_angle=start,
                angle=ang,
                fill_color=color,
                fill_opacity=opa,
                stroke_color=stroke_color,
                stroke_width=stroke_width,

            )

            self.sectors.add(share_sector)

            start += ang

        self.add(self.sectors, self.fake_circle)
