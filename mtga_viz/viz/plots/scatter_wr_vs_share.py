from manim import *
from mtga_viz.viz.objects.pin import *
from mtga_viz.viz.utils.constants_viz import ARCH_COLORS
from mtga_viz.viz.objects.scatter_wr_vs_share import Scatter_WR


MathTex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)
Tex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)


class SimpleScatter(Scene):
    def construct(self):
        plot = Scatter_WR(summary_archetype, margins=3, spacing=5)
        plot.scale_to_fit_height(config.frame_height - 2)
        plot.to_corner(DL)
        self.add(plot)
