from manim import *
from mtga_viz.viz.utils.cut_out import *
from mtga_viz.viz.utils.parser import *


class Pin(Group):
    def __init__(
        self,
        label: str,
        color_label: ParsableManimColor = BLUE,
        opa: float = 0.9,
        stroke_width: float = 3,
        ** kwargs
    ):
        super().__init__(**kwargs)

        self.cut = Circle(fill_opacity=1, radius=2, stroke_color=color_label, stroke_width=0)
        self.img = ImageMobject(f'source_pics/{simple_parser(label)}')
        self.test = clip_image_to_mobject(self.img, self.cut)
        self.border = Circle(radius=self.cut.get_width()/4,
                             stroke_color=color_label,
                             stroke_width=stroke_width,
                             stroke_opacity=opa)
        self.test.scale_to_fit_height(self.border.get_height()-0.3)

        self.final_pin = Group(self.test, self.border).scale(0.3)
        self.add(self.final_pin)
