from manim import *
from mtga_viz.viz.objects.legend_matrix import Legend_Matrix
from mtga_viz.viz.utils.load import load_data_plot
from mtga_viz.viz.utils.constants_viz import BG_COLOR, TEXT_PRIMARY
from mtga_viz.viz.objects.match_matrix import MatchupMatrix
from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.plots.template import *


class MatchupMatrixScene(Scene):
    DATA_DIR = None
    SOURCE = None

    def construct(self):
        self.camera.background_color = BG_COLOR

        data = load_data_plot(self.DATA_DIR)
        matrix_dict = data["matrix"]
        wr_dict = data["wr_interval"]
        general_data_dict = data["general"]

        title = Tex(
            f"Matchup Matrix (Top {matrix_dict['n_rows']})",
            color=TEXT_PRIMARY,
            font_size=43,
        ).to_edge(UL)

        matrix = MatchupMatrix(
            matrix_dict=matrix_dict,
            wr_dict=wr_dict,
            buff=0.1,
            frame_height=config.frame_height - 1,
        ).move_to(ORIGIN).shift(0.2*DOWN)

        info = InfoBox(
            source=f"{self.SOURCE}",
            start_date=general_data_dict["start_date"],
            end_date=general_data_dict["end_date"],
            samples=wr_dict["total_matches"],
            comment="\\# of Matches",
            font_size=15,
        ).next_to(title, RIGHT)

        legend = Legend_Matrix(title='Opacity shows match confidence').to_corner(DR, buff=0.2)

        self.add(title, matrix, info, legend)
