from manim import *
from mtga_viz.viz.constants import ARCH_COLORS, RESULT_COLORS
from mtga_viz.viz.pin import Pin


class ResultHistogram(Group):
    def __init__(
        self,
        df,
        category_col,
        result_cols=("2-0", "2-1", "1-2", "0-2"),
        color_map=None,
        height_bar: float = 0.6,
        stroke_width: float = 1,
        **kwargs,
    ):
        """
        Simple piled histogram to count how many games end up 2-0, 2-1, and so on against a given deck or archetype.

        Args:
            df (_type_): The dataframe to extract information from.
            category_col (_type_): The category one wants to explore.
            result_cols (tuple, optional): Defaults to ("2-0", "2-1", "1-2", "0-2").
            color_map (_type_, optional): The associated color to each result. Defaults to None.
            height_bar (float, optional): Defaults to 0.6.
            stroke_width (float, optional): Defaults to 1.
        """
        super().__init__(**kwargs)

        self.df = df
        self.category_col = category_col
        self.result_cols = result_cols
        self.color_map = color_map or ARCH_COLORS

        x_max = df[list(result_cols)].sum(axis=1).max()

        self.axes = Axes(
            x_range=[0, x_max, 5],
            y_range=[0, len(df), 1],
            x_length=4,
            y_length=6,
            tips=False,
            axis_config={"include_ticks": False, "color": GREY},
            x_axis_config={"stroke_opacity": 0},
            y_axis_config={"stroke_opacity": 0},
        ).set_z_index(10)

        bars = Group()
        pins = Group()
        values = Group()
        tags = Group()

        for i, (_, row) in enumerate(df.iterrows()):
            x0 = 0
            row_rects = []

            for col in result_cols:
                w = row[col]
                if w == 0:
                    continue

                color = self.result_color(col)
                rect = Rectangle(
                    width=self.axes.c2p(w, 0)[0] - self.axes.c2p(0, 0)[0],
                    height=height_bar,
                    fill_color=color,
                    fill_opacity=0.5,
                    stroke_color=color,
                    stroke_width=stroke_width,
                )
                rect.move_to(self.axes.c2p(x0 + w / 2, i + 0.5))
                bars.add(rect)
                row_rects.append((col, rect))

                if w >= 2:
                    val = Tex(str(int(w)), color=WHITE).scale(0.7)
                    val.move_to(rect.get_center())
                    val.set_z_index(10)
                    values.add(val)

                x0 += w

            if i == 0 and row_rects:
                top_y = max(rect.get_top()[1] for _, rect in row_rects)
                for col, rect in row_rects:
                    tag = self._tag(col)
                    tag.move_to([rect.get_center()[0], top_y + 0.18, 0])
                    tags.add(tag)

            pin = Pin(
                label=str(row[category_col]),
                color_label=self.color_map[str(row[category_col])],
                stroke_width=1.5,
            )
            pin.next_to(self.axes.c2p(0, i + 0.5), LEFT, buff=0.2)
            pins.add(pin)

        self.add(self.axes, bars, values, pins, tags)

    def _tag(self, text):
        label = Tex(text, color=WHITE).scale(0.45)
        bg = BackgroundRectangle(
            label,
            color=self.result_color(text),
            buff=0.05,
            fill_opacity=0.18,
        )
        return Group(bg, label).set_z_index(20)

    @staticmethod
    def result_color(result):
        return RESULT_COLORS[result]
