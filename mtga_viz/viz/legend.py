from manim import *
from mtga_viz.viz.pin import Pin
from mtga_viz.viz.utils.parser import underscore_parser


class Legend(Group):
    def __init__(
        self,
        labels: list,
        shares_pct: list,
        colors_dict: dict,
        font_size: float = 25,
        stroke_width: float = 2,
        direction: str = "vertical",   # "vertical" or "horizontal"
        show_text: bool = True,
        show_pct_symbol: bool = True,
        pin_scale: float = 1.0,
        item_buff: float = 0.15,
        group_buff: float = 0.2,
        **kwargs,
    ):
        """
        This object creates a visual legend, that can be chosen vertical or horizontal, that may contain information about decks or archetypes of the meta you want to display.

        Args:
            labels (list): The names of decks to explore. It should coincide with names of pictures to display.
            shares_pct (list): The list of % share.
            colors_dict (dict):The colors associated to each deck/archetype.
            font_size (float, optional): The font size. Defaults to 25.
            stroke_width (float, optional): Defaults to 2.
            direction (str, optional): Direction for the legend to be displayed. Defaults to "vertical".
            show_pct_symbol (bool, optional): Show or not the % symbol. Defaults to True.
            pin_scale (float, optional): Defaults to 1.0.
            item_buff (float, optional): Defaults to 0.15.
            group_buff (float, optional): Defaults to 0.2.

        """
        super().__init__(**kwargs)

        if len(shares_pct) != len(labels):
            raise ValueError("shares_pct must have the same length as labels.")

        colors = [colors_dict[k] for k in labels]

        outer_dir = DOWN if direction == "vertical" else RIGHT
        outer_align = LEFT if direction == "vertical" else UP

        items = Group(*[
            self._make_item(
                lab=lab,
                ptc=ptc,
                col=col,
                font_size=font_size,
                stroke_width=stroke_width,
                direction=direction,
                show_text=show_text,
                show_pct_symbol=show_pct_symbol,
                pin_scale=pin_scale,
                item_buff=item_buff,
            )
            for lab, ptc, col in zip(labels, shares_pct, colors)
        ])

        items.arrange(outer_dir, aligned_edge=outer_align, buff=group_buff)
        self.add(items)

    @staticmethod
    def _make_item(
        lab,
        ptc,
        col,
        font_size,
        stroke_width,
        direction,
        show_text,
        show_pct_symbol,
        pin_scale,
        item_buff,
    ):

        pin = Pin(label=lab, color_label=col, stroke_width=stroke_width).scale(pin_scale)

        pct_text = f"{ptc}\\,\\%" if show_pct_symbol else f"{ptc}"
        pct = MathTex(pct_text, font_size=0.8 * font_size)

        content_parts = []
        if show_text:
            content_parts.append(Tex(f"{underscore_parser(lab)}", color=col, font_size=0.8*font_size))
        content_parts.append(pct)

        if direction == "vertical":
            content = Group(*content_parts).arrange(RIGHT, buff=0.1)
            return Group(pin, content).arrange(RIGHT, buff=item_buff)

        content = Group(*content_parts).arrange(DOWN, buff=0.1)
        return Group(pin, content).arrange(DOWN, buff=item_buff)
