
from manim import *
from mtga_viz.viz.utils.constants_viz import CONFIDENCE_COLORS, TEXT_PRIMARY, TEXT_SECONDARY


class Legend_Confidence(Group):
    def __init__(
        self,
        font_size: float = 10,
        buff: float = 0.2,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.caption = Tex("Colors show 95\\% confidence", font_size=font_size, color=TEXT_PRIMARY)

        self.conf_tags = Group()

        for conf in CONFIDENCE_COLORS.keys():
            tex = Tex(f"{conf}", font_size=font_size, color=TEXT_SECONDARY)
            dot = Dot(color=CONFIDENCE_COLORS[conf])
            self.conf_tags.add(VGroup(dot, tex).arrange(RIGHT, buff=0.1))

        self.conf_tags.arrange(DOWN, aligned_edge=LEFT)
        self.caption.next_to(self.conf_tags, UP, buff=buff)

        self.add(self.caption, self.conf_tags)
