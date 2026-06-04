from manim import *


class FramedPlot(Group):
    def __init__(
        self,
        mobj,
        title,
        buff=0.3,
        top_extra=0.6,
        corner_radius=0.1,
        title_buff=0.2,
        title_font_size=35,
        frame_color=GREY_B,
        title_color=WHITE,
        stroke_width=2,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.frame = SurroundingRectangle(
            mobj,
            buff=buff,
            color=frame_color,
            stroke_width=stroke_width,
            corner_radius=corner_radius,
        )

        old_bottom = self.frame.get_bottom()
        self.frame.stretch_to_fit_height(self.frame.height + top_extra)
        self.frame.align_to(old_bottom, DOWN)

        self.title = Tex(
            title,
            color=title_color,
            font_size=title_font_size,
        )

        self.title.move_to(
            self.frame.get_top() + DOWN * (self.title.height / 2 + title_buff)
        )

        self.add(self.frame, self.title, mobj)
