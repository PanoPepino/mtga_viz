from manim import *

from mtga_viz.viz.utils.constants_viz import BG_COLOR, TEXT_PRIMARY, TEXT_SECONDARY


class InfoBox(VGroup):
    def __init__(
        self,
        start_date: str,
        end_date: str,
        samples: int,
        source: str = "Tournaments \\& League",
        comment: str = "Number of Matches",
        font_size: int = 15,
        tex_color=TEXT_PRIMARY,
        secondary_color=TEXT_SECONDARY,
        box_color=TEXT_SECONDARY,
        corner_radius: float = 0.15,
        stroke_width: float = 1.2,
        buff_box: float = 0.1,
        **kwargs
    ):
        """
        Simple source/date info box for plots.

        Args:
            start_date (str): Start date to display.
            end_date (str): End date to display.
            source (str, optional): Source label. Defaults to "MTGMelee & League".
            comment (str, optional): Extra comment shown at the end of the line.
                Defaults to "Tournament and league data".
            font_size (int, optional): Font size. Defaults to 24.
            tex_color (_type_, optional): Main tex color.
            secondary_color (_type_, optional): Secondary tex color.
            box_color (_type_, optional): Border color of the rounded rectangle.
            corner_radius (float, optional): Rounded rectangle corner radius.
                Defaults to 0.15.
            stroke_width (float, optional): Border width. Defaults to 1.2.
            buff_tex (float, optional): Horizontal spacing between tex chunks.
                Defaults to 0.3.
            buff_box (float, optional): Padding between tex and box.
                Defaults to 0.2.
        """

        super().__init__(**kwargs)

        self.source_text = Tex("Source: ",
                               f"{source}",
                               " \\quad ",
                               f"{comment}: ",
                               f"{samples/2}",
                               " \\quad ",
                               font_size=font_size, color=secondary_color)
        self.source_text[1].set_color(tex_color)
        self.source_text[4].set_color(tex_color)

        self.date_text = Tex("start date: ",
                             f"{start_date}",
                             " \\quad ",
                             f"end date: ",
                             f"{end_date}",
                             font_size=font_size, color=secondary_color)

        self.date_text[1].set_color(tex_color)
        self.date_text[4].set_color(tex_color)

        self.text = VGroup(self.source_text, self.date_text).arrange(RIGHT, buff=2*buff_box, aligned_edge=UP)

        self.box = SurroundingRectangle(self.text,
                                        corner_radius=corner_radius,
                                        color=box_color,
                                        stroke_width=stroke_width,
                                        buff=buff_box
                                        )

        self.add(self.box, self.text)
