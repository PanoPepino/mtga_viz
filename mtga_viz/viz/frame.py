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
        """
        Creates a simple Surrounding rectangle to a given object and add a title to it.

        Args:
            mobj (_type_): The object.
            title (_type_): The title to add at the top.
            buff (float, optional): How title the surrounding is to the object.
            top_extra (float, optional): Add a little bit of buff at top to add title.
            corner_radius (float, optional): If rounded corners or not.
            title_buff (float, optional): How close the title is to the top of the surrounding.
            title_font_size (int, optional): How big the title reads.
            frame_color (_type_, optional): 
            title_color (_type_, optional): 
            stroke_width (int, optional):
        """

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
