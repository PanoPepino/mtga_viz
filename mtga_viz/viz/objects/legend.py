from manim import *
from mtga_viz.viz.objects.pin import Pin
from mtga_viz.viz.utils.parser import capitalise_no_score


class Legend(Group):
    def __init__(
        self,
        labels: list,
        shares_pct: list | None = None,
        colors_dict: dict = None,
        font_size: float = 25,
        stroke_width: float = 2,
        arrange_in_grid: bool = False,
        grid_rows: int | None = None,
        grid_cols: int | None = None,
        item_order: str = "pin_text",    # "pin_text" | "text_pin"
        text_direction=RIGHT,            # direction inside text block
        pct_position: str = "after",     # "after" | "before"
        show_text: bool = True,
        show_pct_symbol: bool = True,
        pin_scale: float = 1.0,
        item_buff: float = 0.15,
        text_buff: float = 0.1,
        group_buff: float = 0.2,
        ndigits: int | None = 2,
        **kwargs,
    ):
        """
        This object creates a visual legend, that may contain information about
        decks or archetypes of the meta you want to display. The legend items
        can optionally be arranged in a grid.




        Args:
            labels (list): The names of decks to explore. It should coincide with names of pictures to display.
            shares_pct (list | None, optional): The list of % share. If not provided, no percentage is displayed. Defaults to None.
            colors_dict (dict):The colors associated to each deck/archetype.
            font_size (float, optional): The font size. Defaults to 25.
            stroke_width (float, optional): Defaults to 2.
            arrange_in_grid (bool, optional): Whether to arrange the legend items in a grid. Defaults to False.
            grid_rows (int | None, optional): Number of rows to use when arranging in a grid. Defaults to None.
            grid_cols (int | None, optional): Number of columns to use when arranging in a grid. Defaults to None.
            item_order (str, optional): Order of the components inside each legend item. It can be "pin_text" or "text_pin". Defaults to "pin_text".
            text_direction (np.ndarray, optional): Direction used to arrange the label and the percentage inside the text block. For example, RIGHT, LEFT, UP or DOWN. Defaults to RIGHT.
            pct_position (str, optional): Whether the percentage is displayed before or after the label. It can be "before" or "after". Defaults to "after".
            show_text (bool, optional): Whether to show the deck/archetype label. Defaults to True.
            show_pct_symbol (bool, optional): Show or not the % symbol. Defaults to True.
            pin_scale (float, optional): Defaults to 1.0.
            item_buff (float, optional): Defaults to 0.15.
            text_buff (float, optional): Spacing between label and percentage inside the text block. Defaults to 0.1.
            group_buff (float, optional): Defaults to 0.2.
            ndigits (int | None, optional): Number of decimal digits used to display the percentage. If None, no rounding is applied. Defaults to 2.




        """
        super().__init__(**kwargs)

        if colors_dict is None:
            colors_dict = {}

        if shares_pct is not None and len(shares_pct) != len(labels):
            raise ValueError("shares_pct must have the same length as labels.")

        if item_order not in {"pin_text", "text_pin"}:
            raise ValueError("item_order must be 'pin_text' or 'text_pin'.")

        if pct_position not in {"before", "after"}:
            raise ValueError("pct_position must be 'before' or 'after'.")

        items = Group(*[
            self._make_item(
                lab=lab,
                ptc=None if shares_pct is None else ptc,
                colors_dict=colors_dict,
                font_size=font_size,
                stroke_width=stroke_width,
                item_order=item_order,
                text_direction=text_direction,
                pct_position=pct_position,
                show_text=show_text,
                show_pct_symbol=show_pct_symbol,
                pin_scale=pin_scale,
                item_buff=item_buff,
                text_buff=text_buff,
                ndigits=ndigits,
            )
            for lab, ptc in zip(labels, shares_pct if shares_pct is not None else [None] * len(labels))
        ])

        if arrange_in_grid and grid_cols is not None and grid_cols > 1:
            cols = []
            n_items = len(items)
            n_rows = grid_rows if grid_rows is not None else int(np.ceil(n_items / grid_cols))

            for j in range(grid_cols):
                start = j * n_rows
                end = min((j + 1) * n_rows, n_items)
                if start >= n_items:
                    break

                col_items = Group(*items[start:end])

                outer_align = LEFT if item_order == "pin_text" else RIGHT
                col_items.arrange(DOWN, aligned_edge=outer_align, buff=group_buff)
                cols.append(col_items)

            items = Group(*cols).arrange(RIGHT, aligned_edge=UP, buff=group_buff)

        elif arrange_in_grid and grid_rows is not None and grid_rows > 1:
            rows = []
            n_items = len(items)
            n_cols = grid_cols if grid_cols is not None else int(np.ceil(n_items / grid_rows))

            for i in range(grid_rows):
                row_items = []
                for j in range(n_cols):
                    idx = j * grid_rows + i
                    if idx < n_items:
                        row_items.append(items[idx])

                if row_items:
                    row_group = Group(*row_items)
                    rows.append(row_group)

            items = Group(*rows).arrange(DOWN, aligned_edge=LEFT, buff=group_buff)
            for row_group in items:
                row_group.arrange(RIGHT, aligned_edge=UP, buff=group_buff)

        else:
            outer_align = LEFT if item_order == "pin_text" else RIGHT
            items.arrange(DOWN, aligned_edge=outer_align, buff=group_buff)

        self.add(items)

    @staticmethod
    def _format_pct(ptc, ndigits, show_pct_symbol):
        if ptc is None:
            return None
        if ndigits is not None:
            ptc = round(ptc, ndigits)
        pct_text = f"{ptc}"
        if show_pct_symbol:
            pct_text += r"\,\%"
        return pct_text

    @staticmethod
    def _make_item(
        lab,
        ptc,
        colors_dict,
        font_size,
        stroke_width,
        item_order,
        text_direction,
        pct_position,
        show_text,
        show_pct_symbol,
        pin_scale,
        item_buff,
        text_buff,
        ndigits,
    ):
        col = colors_dict.get(lab, WHITE)

        pin = Pin(
            label=lab,
            color_label=colors_dict,
            stroke_width=stroke_width,
        ).scale(pin_scale)

        content_parts = []

        if show_text:
            label_mob = Tex(
                f"{capitalise_no_score(lab)}",
                color=col,
                font_size=0.8 * font_size,
            )
            content_parts.append(label_mob)

        pct_text = Legend._format_pct(ptc, ndigits, show_pct_symbol)
        if pct_text is not None:
            pct_mob = MathTex(
                pct_text,
                font_size=0.9 * font_size,
            )
            if show_text:
                if pct_position == "before":
                    content_parts = [pct_mob] + content_parts
                else:
                    content_parts = content_parts + [pct_mob]
            else:
                content_parts = [pct_mob]

        if not content_parts:
            return Group(pin)

        content = Group(*content_parts).arrange(text_direction, buff=text_buff)

        if item_order == "pin_text":
            return Group(pin, content).arrange(RIGHT, buff=item_buff)
        else:
            content.next_to(pin, LEFT, buff=item_buff)
            item = Group(content, pin)
            return item
