from manim import *

from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.objects.pie_chart import PieChart
from mtga_viz.viz.utils.constants_viz import TEXT_PRIMARY, TEXT_SECONDARY

MathTex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)
Tex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)

template= {
    "opa":0.6,
    "rcorner":0.1,
    "stroke_w":1.5,
    "title_font":50,
    "small_font":15,
    "main_text_color":TEXT_PRIMARY,
    "second_text_color":TEXT_SECONDARY,
    "buff":0.1,

}

# PieChart

PieChart.set_default(
    inner_rad=0.3,
    outer_rad=3,
    opa=template['opa'],
    stroke_color=TEXT_PRIMARY,
    stroke_width=template['stroke_w']
)

InfoBox.set_default(
    font_size=template['small_font'],
    tex_color= template['main_text_color'],
    secondary_color=template['second_text_color'],
    box_color=template['second_text_color'],
    corner_radius=template['rcorner'],
    stroke_width=template['stroke_w'],
    buff_box=template['buff']
)