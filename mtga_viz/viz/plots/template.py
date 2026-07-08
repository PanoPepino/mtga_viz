from manim import *
from mtga_viz.viz.objects.deck_histo import DeckShareHistogram
from mtga_viz.viz.objects.deck_wr_error import DeckWRErrorPlot
from mtga_viz.viz.objects.info_box import InfoBox
from mtga_viz.viz.objects.legend import Legend
from mtga_viz.viz.objects.pie_chart import PieChart
from mtga_viz.viz.objects.scatter_wr_vs_share import Scatter_WR
from mtga_viz.viz.objects.tile import Tile
from mtga_viz.viz.utils.constants_viz import TEXT_PRIMARY, TEXT_SECONDARY

MathTex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)
Tex.set_default(tex_template=TexFontTemplates.comfortaa, font_size=25)

template = {
    "opa": 0.6,
    "opa_axis": 0.2,
    "rcorner": 0.05,
    "stroke_w": 1,
    "title_font": 45,
    "mid_font": 30,
    "small_font": 15,
    "footnote_font": 10,
    "main_text_color": TEXT_PRIMARY,
    "second_text_color": TEXT_SECONDARY,
    "buff": 0.1,

}

# PieChart
PieChart.set_default(
    inner_rad=2,
    outer_rad=3,
    opa=template['opa'],
    stroke_color=TEXT_PRIMARY,
    stroke_width=template['stroke_w']
)

InfoBox.set_default(
    font_size=template['small_font'],
    tex_color=template['main_text_color'],
    secondary_color=template['second_text_color'],
    box_color=template['second_text_color'],
    corner_radius=template['rcorner'],
    stroke_width=template['stroke_w'],
    buff_box=template['buff']
)

Legend.set_default(
    stroke_width=2*template['stroke_w'],
    group_buff=template['buff']

)

# Deckhisto

DeckShareHistogram.set_default(
    bar_fill_opacity=template['opa'],
    corner_rad=template['rcorner'],
    stroke_width=template['stroke_w'],
    stroke_opacity=template['opa_axis']

)

# ScatterWR

Scatter_WR.set_default(
    stroke_w=template['stroke_w'],
    buff=template['buff'],
    corner_rad=template['rcorner']
)

# Deck with error

DeckWRErrorPlot.set_default(
    stroke_width=template['stroke_w'],
    buff=template['buff'],
    stroke_opacity=template['opa_axis']
)

# MatchMatrix

Tile.set_default(
    str_width=template['stroke_w'],
    opa=template['opa_axis'],
    crad=template['rcorner'],
    width=2
)
