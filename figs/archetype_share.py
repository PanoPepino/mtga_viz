

from manim import *
from mtga_viz.viz.constants import *
from mtga_viz.viz.pie_chart import Pie_Sectors
from mtga_viz.viz.legend import Legend
from dataframes import summary_archetype


MathTex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)
Tex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)


class test_class(Scene):
    def construct(self):
        test = Pie_Sectors(inner_rad=0.5,
                           outer_rad=2.5,
                           labels=summary_archetype['archetype'],
                           shares_rad=summary_archetype['share_rad'],
                           colors_dict=ARCH_COLORS,
                           opa=0.7)

        title = Tex("What Archetypes does a Shadow player see in the Ladder?", font_size=40)
        title.to_corner(UP)

        legend = Legend(
            labels=summary_archetype['archetype'],
            shares_pct=summary_archetype['share_pct'],
            colors_dict=ARCH_COLORS,
            direction="vertical",
            show_text=True,
            item_buff=0.2
        )

        self.add(title, legend.to_corner(DL), test.shift(2*RIGHT))
