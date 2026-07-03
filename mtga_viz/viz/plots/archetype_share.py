from manim import *

from mtga_viz.viz.utils.load import load_json
from mtga_viz.viz.utils.constants_viz import BG_COLOR, TEXT_PRIMARY
from mtga_viz.viz.objects.pie_chart import PieChart
from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.objects.legend import Legend
from mtga_viz.viz.plots.template import *


class ArchShareScene(Scene):
    CONFIG_PATH = None

    def load_data(self):
        if self.CONFIG_PATH is None:
            raise ValueError("CONFIG_PATH must be defined in subclass.")

        cfg = load_json(self.CONFIG_PATH)
        plot_dict = load_json(cfg["plot_path"])
        general_data_dict = load_json(cfg["general_data_path"])
        return cfg, plot_dict, general_data_dict

    def construct(self):
        self.camera.background_color = BG_COLOR

        cfg, plot_dict, general_data_dict = self.load_data()

        title = Tex(
            "Archetype Share",
            color=TEXT_PRIMARY,
            font_size=50,
        ).to_edge(UL)

        pie = PieChart(
            labels=plot_dict["labels"],
            shares_rad=plot_dict["shares_rad"],
            colors_dict=plot_dict["colors_dict"]
        ).to_corner(DL)

        legend = Legend(
            labels=plot_dict["labels"],
            shares_pct=plot_dict["shares_pct"],
            colors_dict=plot_dict["colors_dict"]
        ).scale_to_fit_height(pie.get_height()).next_to(pie, RIGHT).shift(2.5 * RIGHT)

        info = InfoBox(
            start_date=general_data_dict["start_date"],
            end_date=general_data_dict["end_date"],
            samples=general_data_dict["n_samples"],
            font_size=15
        ).next_to(title, RIGHT)

        self.add(title, pie, legend, info)
