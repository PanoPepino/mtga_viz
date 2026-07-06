from manim import *
from pathlib import Path

from mtga_viz.viz.utils.load import load_json, load_data_plot
from mtga_viz.viz.utils.constants_viz import BG_COLOR, TEXT_PRIMARY
from mtga_viz.viz.objects.pie_chart import PieChart
from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.objects.legend import Legend
from mtga_viz.viz.plots.template import *


class ArchShareScene(Scene):
    DATA_DIR = None  # folder that contains json files

    def construct(self):
        self.camera.background_color = BG_COLOR

        data = load_data_plot(self.DATA_DIR)

        plot_dict = data["arch"]      # arch.json
        general_data_dict = data["general"]   # general.json

        title = Tex(
            "Archetype Share",
            color=TEXT_PRIMARY,
            font_size=45,
        ).to_edge(UL)

        pie = PieChart(
            labels=plot_dict["labels"],
            shares_rad=plot_dict["shares_rad"],
            colors_dict=plot_dict["colors_dict"]
        ).to_corner(DL)

        legend = Legend(
            labels=plot_dict["labels"],
            shares_pct=plot_dict["shares_pct"],
            colors_dict=plot_dict["colors_dict"],
            item_order='text_pin'
        ).scale_to_fit_height(pie.get_height()).next_to(pie, RIGHT).shift(2.5 * RIGHT)

        info = InfoBox(
            start_date=general_data_dict["start_date"],
            end_date=general_data_dict["end_date"],
            samples=plot_dict["total"],
            font_size=15,
            comment='\\# of Decks'
        ).next_to(title, RIGHT)

        self.add(title, pie, legend, info)
