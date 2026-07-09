from manim import *
from mtga_viz import *
from mtga_viz.viz.objects.pin import Pin
from mtga_viz.viz.utils.constants_viz import TEXT_PRIMARY, TEXT_SECONDARY, RUN_RESULT_COLORS
from mtga_viz.viz.utils.parser import capitalise_no_score


class ResultHistogram(Group):
    def __init__(
        self,
        runs_dict,
        result_cols=RUN_RESULT_COLORS.keys(),
        category_col="user_deck",
        total_col="total_runs",
        x_length=7,
        y_step=0.55,
        height_bar=0.4,
        font_size=25,
        pin_scale=0.65,
        buff=0.2,
        stroke_width=1,
        x_tick_step=10,
        crad: float = 0.05,
        stroke_opacity=0.2,
        fill_opacity=0.5,
        top_tag_font_size=15,
        pct_font_size=10,
        min_pct_label_width=0.3,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.runs_dict = runs_dict
        self.result_cols = tuple(result_cols)
        self.category_col = category_col
        self.total_col = total_col

        self.labels = [row[category_col] for row in runs_dict]
        self.total_runs = [row[total_col] for row in runs_dict]
        self.results = {
            col: [float(row.get(col, 0)) for row in runs_dict]
            for col in self.result_cols
        }

        n = len(self.labels)

        self.axes = NumberPlane(
            x_range=[0, 100, x_tick_step],
            y_range=[0, n, 1],
            x_length=x_length,
            y_length=n * y_step,
            tips=False,
            axis_config={
                "include_ticks": False,
                "color": TEXT_SECONDARY,
                "stroke_opacity": stroke_opacity,
            },
            y_axis_config={"stroke_opacity": 0},
            background_line_style={
                "stroke_color": TEXT_SECONDARY,
                "stroke_opacity": 0.0,
            },
            x_axis_config={
                "stroke_opacity": 0.0,
            },
        ).set_z_index(0)

        bar_group = Group()
        pin_group = Group()
        label_group = Group()
        total_group = Group()
        first_row_tag_group = Group()
        pct_group = Group()

        for i, lab in enumerate(self.labels):
            y = n - i - 0.5
            x_left = 0

            for col in self.result_cols:
                w = self.results[col][i]
                if w <= 0:
                    continue

                rect = RoundedRectangle(
                    width=self.axes.c2p(w, 0)[0] - self.axes.c2p(0, 0)[0],
                    height=height_bar,
                    corner_radius=crad,
                    fill_color=RUN_RESULT_COLORS[col],
                    fill_opacity=fill_opacity,
                    stroke_color=RUN_RESULT_COLORS[col],
                    stroke_width=stroke_width,
                )
                rect.move_to(self.axes.c2p(x_left + w / 2, y))
                bar_group.add(rect)

                pct_text = MathTex(
                    rf"{w:.0f}\%",
                    font_size=pct_font_size,
                    color=TEXT_PRIMARY,
                )
                if rect.width >= max(min_pct_label_width, pct_text.width + 0.04):
                    pct_text.next_to(rect.get_corner(DL), UR, buff=0.05)
                    pct_group.add(pct_text)

                if i == 0:
                    top_tag = Tex(
                        self.pretty_result_label(col),
                        color=RUN_RESULT_COLORS[col],
                        font_size=top_tag_font_size,
                    )
                    top_tag.next_to(rect, UP, buff=0.08)
                    first_row_tag_group.add(top_tag)

                x_left += w

            pin = Pin(
                label=lab,
                color_label=ARCH_COLORS,
                stroke_width=stroke_width,
            ).scale(pin_scale)
            pin.next_to(self.axes.c2p(0, y), LEFT, buff=buff)

            text = Tex(
                capitalise_no_score(lab),
                color=TEXT_PRIMARY,
                font_size=font_size,
            ).next_to(pin, LEFT, buff=buff)

            self.total_text = MathTex(
                str(int(self.total_runs[i])),
                font_size=font_size * 0.7,
                color=TEXT_SECONDARY,
            ).next_to(self.axes.c2p(100, y), RIGHT, buff=0.2)

            pin_group.add(pin)
            label_group.add(text)
            total_group.add(self.total_text)

        self.add(
            self.axes,
            bar_group,
            pct_group,
            first_row_tag_group,
            pin_group,
            label_group,
            total_group,
        )

    @staticmethod
    def pretty_result_label(col):
        wins = int(col.split("_")[0])
        losses = 0 if wins == 7 else 1
        return f"{wins}-{losses}"
