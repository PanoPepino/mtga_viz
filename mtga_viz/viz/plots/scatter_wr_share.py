from manim import *

from mtga_viz.viz.utils.load import load_data_plot
from mtga_viz.viz.utils.constants_viz import BG_COLOR, TEXT_PRIMARY, ARCH_COLORS
from mtga_viz.viz.objects.scatter_wr_vs_share import Scatter_WR
from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.objects.legend import Legend


class ScatterWRScene(Scene):
    DATA_DIR = None
    SOURCE = None

    def construct(self):
        self.camera.background_color = BG_COLOR

        data = load_data_plot(self.DATA_DIR)
        plot_dict = data['decks']
        wr_dict = data['wr_interval']
        general_data_dict = data['general']

        title = Tex(
            f"Presence vs WR (Top {plot_dict['top_n']})",
            color=TEXT_PRIMARY,
            font_size=40,
        ).to_edge(UL)

        scatter = Scatter_WR(
            share_plot_dict=plot_dict,
            wr_plot_dict=wr_dict,
            color_map=ARCH_COLORS,
            scale_tag=0.7,
        ).scale(0.9).next_to(title, DOWN, aligned_edge=LEFT, buff=0.4)

        info = InfoBox(
            source=f"{self.SOURCE}",
            start_date=general_data_dict["start_date"],
            end_date=general_data_dict["end_date"],
            samples=wr_dict["total_matches"],
            comment='\\# of Matches',
            font_size=15
        ).next_to(title, RIGHT)

        legend = Legend(
            labels=wr_dict["labels"],
            item_order='pin_text',
            arrange_in_grid=True,
            grid_cols=2,
            group_buff=0.2
        ).scale_to_fit_height(scatter.frame.get_height()-1).next_to(scatter, RIGHT, buff=0.4)

        self.add(title, scatter, legend, info)
