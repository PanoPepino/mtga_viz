from manim import *

from mtga_viz.viz.utils.constants_viz import TEXT_PRIMARY


class PieChart(VGroup):
    def __init__(
        self,
        labels: list,
        shares_rad: list,
        colors_dict: dict,
        inner_rad: float = 0,
        outer_rad: float = 2,
        opa: float = 0.6,
        stroke_color=TEXT_PRIMARY,
        stroke_width: float = 2.5,
        **kwargs
    ):
        """
        Simple Pie Chart to display shares.


        Args:
            labels (list): The list of archetypes or decks you want to display.
            shares_rad (list): The column of DataFrame with % converted to radians.
            colors_dict (dict): The associated colors to each arch/deck.
            inner_rad (float, optional): The inner radius of the annulus. Defaults to 0.
            outer_rad (float, optional): The outer radious of annulus. Defaults to 2.
            opa (float, optional): Opacity. Defaults to 0.6.
            stroke_color (_type_, optional): Defaults to WHITE.
            stroke_width (float, optional): Defaults to 1.5.
        """

        super().__init__(**kwargs)

        self.sectors = VGroup()

        angles = [float(x) for x in shares_rad]
        colors = [colors_dict[k] for k in labels]

        start = 0.0
        for ang, color in zip(angles, colors):
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

        self.add(self.sectors)
