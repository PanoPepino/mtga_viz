
from manim import *
from mtga_viz.viz.utils.constants_viz import TEXT_PRIMARY, TEXT_SECONDARY, WR_COLORS, WR_CONFIDENCE


class Legend_Matrix(Group):
    def __init__(
        self,
        title: str = None,
        font_size: float = 10,
        buff: float = 0.2,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.caption = Tex(f"{title}", font_size=font_size, color=TEXT_PRIMARY)

        self.conf_tags = Group()

        for conf in WR_CONFIDENCE.keys():
            tex = Tex(f"{conf}", font_size=font_size, color=TEXT_SECONDARY)
            dot_win = Dot(color=WR_COLORS['win'], radius=0.03)
            dot_draw = Dot(color=WR_COLORS['draw'], radius=0.03)
            dot_lose = Dot(color=WR_COLORS['lose'], radius=0.03)

            self.conf_tags.add(VGroup(dot_win, dot_draw, dot_lose, tex).set_opacity(
                WR_CONFIDENCE[conf]+0.1).arrange(RIGHT, buff=0.1))

        self.conf_tags.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        self.caption.next_to(self.conf_tags, UP, buff=buff, aligned_edge=LEFT)

        self.add(self.caption, self.conf_tags)
