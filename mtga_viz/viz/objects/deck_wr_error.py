from manim import *
from mtga_viz.viz.objects.pin import Pin
from mtga_viz.viz.utils.constants_viz import CONFIDENCE_COLORS, RESULT_COLORS, TEXT_PRIMARY, TEXT_SECONDARY, ARCH_COLORS
from mtga_viz.viz.utils.parser import capitalise_no_score


class DeckWRErrorPlot(Group):
    def __init__(
        self,
        wr_dict,
        colors_dict=None,
        x_length=8,
        y_step=0.6,
        font_size=25,
        spacing_x: float = 5,
        pin_scale=0.8,
        left_buff=0.2,
        stroke_width=2.5,
        x_tick_step=10,
        stroke_opacity=0.2,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.wr_dict = wr_dict
        self.labels = wr_dict["labels"]
        self.wr_low = wr_dict["wr_low"]
        self.wr_high = wr_dict["wr_high"]
        self.confidence = wr_dict['confidence']
        self.wr = wr_dict["wr"]
        self.colors_dict = colors_dict or ARCH_COLORS

        n = len(self.labels)
        x_max = max(self.wr_high)+1
        x_min = min(self.wr_low)-1
        x_numbers = np.arange(x_min+2, x_max, spacing_x)

        self.axes = NumberPlane(
            x_range=[x_min, x_max, x_tick_step],
            y_range=[0, n, 1],
            x_length=x_length,
            y_length=n * y_step,
            tips=False,
            axis_config={"include_ticks": False, "color": TEXT_SECONDARY, "stroke_opacity": 1},
            y_axis_config={"stroke_opacity": 0},
            background_line_style={
                "stroke_color": TEXT_SECONDARY,
                "stroke_opacity": 0.0,
            },
            x_axis_config={
                "stroke_opacity": 0.2,
                "include_numbers": True,
                "numbers_to_include": x_numbers,
                "label_direction": UP,
                "font_size": 8
            },
        ).set_z_index(0)

        v_line = Line(
            start=self.axes.c2p(50, 0),
            end=self.axes.c2p(50, n),
            stroke_color=TEXT_SECONDARY,
            stroke_width=stroke_width,
            stroke_opacity=0.2,
        ).set_z_index(-1)

        axis_labels = self.axes.get_axis_labels(
            x_label=Tex("Win Rate\\,(\\%)", color=WHITE, font_size=20),
            y_label=MathTex("")
        )
        axis_labels[0].next_to(v_line.get_start(), DOWN, buff=0.2)

        wr_50 = Tex('50\\%', font_size=15, color=TEXT_SECONDARY).next_to(v_line.get_end(), UP, buff=0.1)

        label_group = Group()
        pin_group = Group()
        bar_group = Group()
        dash_group = Group()
        wr_point_group = Group()

        for i, (lab, wr, wr_low, wr_high, confidence) in enumerate(zip(self.labels, self.wr, self.wr_low, self.wr_high, self.confidence)):
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

            dash_line = DashedLine(
                start=self.axes.c2p(x_min, y),
                end=self.axes.c2p(x_max, y),
                stroke_width=stroke_width,
                stroke_opacity=stroke_opacity,
                color=TEXT_SECONDARY,
            )

            wr_point = Dot(radius=0.05, point=self.axes.c2p(wr, y))
            wr_interval = Line(start=self.axes.c2p(wr_low, y), end=self.axes.c2p(wr_high, y),
                               stroke_width=0.5, stroke_opacity=0.5)

            wr_base_text = MathTex(
                rf"{wr:.1f}\,\%",
                font_size=15,
                color=TEXT_PRIMARY,
            ).next_to(dash_line.get_end(), RIGHT, buff=0.5, aligned_edge=RIGHT)
            wr_interval_text = MathTex(
                rf"({wr_low:.1f}-{wr_high:.1f}\,\%)",
                font_size=10,
                color=TEXT_SECONDARY,
            ).next_to(dash_line.get_end(), RIGHT, buff=1.3, aligned_edge=RIGHT)

            wr_text = VGroup(wr_base_text, wr_interval_text)

            pin.next_to(self.axes.c2p(x_min, y), LEFT, buff=left_buff)
            text.next_to(pin, LEFT, buff=left_buff)

            label_group.add(text)
            pin_group.add(pin)
            dash_group.add(dash_line)
            wr_point_group.add(VGroup(wr_point, wr_interval, wr_text).set_color(CONFIDENCE_COLORS[confidence]))

        self.add(self.axes, bar_group, pin_group, label_group, v_line, wr_50, axis_labels, dash_group, wr_point_group)
