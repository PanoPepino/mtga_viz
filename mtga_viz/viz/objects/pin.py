from pathlib import Path
from manim import *

from mtga_viz.viz.utils.constants_viz import MTG_COLORS_PIN, ARCH_COLORS
from mtga_viz.viz.utils.cut_out import *
from mtga_viz.viz.utils.parser import *
from mtga_viz.viz.utils.load import get_asset_path


def build_color_ring(
    letters: list[str],
    outer_radius: float = 0.6,
    inner_radius: float = 0.5,
    stroke_width: float = 0,
) -> VGroup:
    """
    Based on a prefix name of the deck, it extracts the colors to create sections representing those colors.
    """
    n = len(letters)
    angle = TAU / n
    ring = VGroup()

    for i, letter in enumerate(letters):
        sector = AnnularSector(
            inner_radius=inner_radius,
            outer_radius=outer_radius,
            angle=angle,
            start_angle=PI / 2 - i * angle,
            fill_color=MTG_COLORS_PIN[letter],
            fill_opacity=0.9,
            stroke_width=stroke_width
        )
        ring.add(sector)

    return ring


class Pin(Group):
    def __init__(
        self,
        label: str,
        format: str = "timeless",
        color_label: dict = ARCH_COLORS,
        opa: float = 0.9,
        stroke_width: float = 2,
        **kwargs
    ):
        """
        Transform a packaged image into a circular visual pin and a border associated to its nature.

        Args:
            label (str): The name of the deck (taken from the DataFrame)
            color_label (ParsableManimColor, optional): The associated color. Defaults to BLUE.
            opa (float, optional): Opacity. Defaults to 0.9.
            stroke_width (float, optional): Defaults to 3.
        """
        super().__init__(**kwargs)

        self.asset_name = simple_parser(label)
        self.asset_path = get_asset_path(format, self.asset_name)

        if not self.asset_path or not Path(self.asset_path).exists():
            self.color_letters = extract_color_letters(self.asset_name)

            self.final_pin = build_color_ring(
                letters=self.color_letters,
                outer_radius=0.22,
                inner_radius=0.14,
            )

            self.add(self.final_pin)
            return

        self.cut = Circle(
            fill_opacity=1,
            radius=2,
            stroke_width=0,
        )

        self.img = ImageMobject(self.asset_path)
        self.test = clip_image_to_mobject(self.img, self.cut)

        self.border_radius = self.cut.get_width() / 4 + 0.1
        self.inner_radius = self.cut.get_width() / 4

        self.inner_border = Circle(
            radius=self.inner_radius,
            stroke_color=WHITE,
            stroke_width=1,
            stroke_opacity=0.8
        )

        self.test.scale_to_fit_height(self.inner_border.get_height())

        if label in color_label:
            self.border = Circle(
                radius=self.border_radius,
                stroke_color=color_label[label],
                stroke_width=stroke_width,
                stroke_opacity=opa
            )

            self.final_pin = Group(
                self.test,
                self.inner_border,
                self.border
            ).scale(0.3)

        else:
            self.color_letters = extract_color_letters(self.asset_name)

            self.sections = build_color_ring(
                letters=self.color_letters,
                outer_radius=self.border_radius + 0.05,
                inner_radius=self.inner_radius + 0.07,
            )

            self.border = Circle(
                radius=self.border_radius,
                stroke_color=WHITE,
                stroke_width=0,
                stroke_opacity=opa,
            )

            self.final_pin = Group(
                self.sections,
                self.test,
                self.inner_border,
                self.border,
            ).scale(0.3)

        self.add(self.final_pin)
