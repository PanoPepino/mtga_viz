from manim import *
from mtga_viz.viz.objects.pin import Pin
from mtga_viz.viz.utils.constants_viz import TEXT_PRIMARY, TEXT_SECONDARY, ARCH_COLORS
from mtga_viz.viz.utils.parser import capitalise_no_score


class DeckShareHistogram(Group):
    def __init__(
        self,
        plot_dict,
        colors_dict=None,
        bar_color=TEXT_PRIMARY,
        bar_fill_opacity=0.5,
        bar_height=0.5,
        x_length=9,
        y_step=0.6,
        font_size=25,
        pct_font_size=25,
        pin_scale=0.8,
        left_buff=0.2,
        right_buff=0.2,
        stroke_width=2,
        x_tick_step=10,
        corner_rad=0.1,
        stroke_opacity=0.2,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.plot_dict = plot_dict
        self.labels = plot_dict["labels"]
        self.counts = plot_dict["counts"]
        self.shares_pct = plot_dict["shares_pct"]
        self.colors_dict = colors_dict or ARCH_COLORS

        n = len(self.labels)
        x_max = max(self.counts)

        self.axes = Axes(
            x_range=[0, x_max, x_tick_step],
            y_range=[0, n, 1],
            x_length=x_length,
            y_length=n * y_step,
            tips=False,
            axis_config={"include_ticks": False, "color": TEXT_SECONDARY},
            x_axis_config={"stroke_opacity": 0},
            y_axis_config={"stroke_opacity": stroke_opacity},
        ).set_z_index(0)

        label_group = Group()
        pin_group = Group()
        bar_group = Group()
        pct_group = Group()

        x0 = self.axes.c2p(0, 0)[0]
        x_unit = self.axes.c2p(1, 0)[0] - self.axes.c2p(0, 0)[0]

        for i, (lab, cnt, pct) in enumerate(zip(self.labels, self.counts, self.shares_pct)):
            y = n - i - 0.5

            text = Tex(
                capitalise_no_score(lab),
                color=TEXT_PRIMARY,
                font_size=font_size,
            )

            pin = Pin(
                label=lab,
                color_label=self.colors_dict,
                stroke_width=stroke_width,
            ).scale(pin_scale)

            bar = RoundedRectangle(
                width=cnt * x_unit,
                height=bar_height,
                fill_color=self.colors_dict.get(lab, bar_color),
                fill_opacity=bar_fill_opacity,
                stroke_color=self.colors_dict.get(lab, bar_color),
                stroke_width=stroke_width,
                corner_radius=corner_rad
            )
            bar.move_to(self.axes.c2p(cnt / 2 + 1, y))

            pct_text = MathTex(
                rf"{pct:.2f}\,\%",
                font_size=pct_font_size,
                color=TEXT_PRIMARY,
            )

            pin.next_to(self.axes.c2p(0, y), LEFT, buff=left_buff)
            text.next_to(pin, LEFT, buff=left_buff)
            pct_text.next_to(bar, RIGHT, buff=right_buff)

            label_group.add(text)
            pin_group.add(pin)
            bar_group.add(bar)
            pct_group.add(pct_text)

        self.add(self.axes, bar_group, pin_group, label_group, pct_group)
