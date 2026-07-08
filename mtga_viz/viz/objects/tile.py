from mtga_viz import *
from manim import *

from mtga_viz.viz.objects.pin import Pin
from mtga_viz.viz.utils.parser import capitalise_no_score
from mtga_viz.viz.utils.constants_viz import TEXT_PRIMARY, TEXT_SECONDARY


class Tile(Group):
    """Visual tile used in matchup matrix layouts.

    Supports header tiles, diagonal markers, matchup cells, and corner cells.
    """

    def __init__(
        self,
        tile_type: str,
        label: str | None = None,
        wr: float | None = None,
        wins: int | None = None,
        losses: int | None = None,
        matches_total: int | None = None,
        wr_total: int | None = None,
        wr_high: int | None = None,
        wr_low: int | None = None,
        confidence: str | None = None,
        width: float = 1.5,
        height: float = 1.5,
        crad: float = 0.1,
        opa: float = 0.3,
        str_width: float = 1,
        pin_scale: float = 0.8,
        **kwargs
    ):
        """Create one matrix tile.

        Args:
            tile_type: Tile variant. Expected values are
                "info_vertical", "info_horizontal", "diagonal",
                "matrix", or "corner".
            label: Deck label shown on info tiles.
            wr: Matchup win rate for matrix tiles.
            wins: Match wins for matrix tiles.
            losses: Match losses for matrix tiles.
            matches_total: Total matches shown on vertical info tiles.
            wr_total: Overall win rate shown on vertical info tiles.
            wr_high: Upper confidence bound for matchup win rate.
            wr_low: Lower confidence bound for matchup win rate.
            confidence: Confidence label used to color matchup tiles.
            width: Tile width.
            height: Tile height.
            crad: Background corner radius.
            opa: Background fill opacity.
            str_width: Background stroke width.
            pin_scale: Scale factor for deck pin icon.
            **kwargs: Extra keyword arguments passed to ``Group``.
        """
        super().__init__(**kwargs)

        self.bg = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=crad,
            fill_opacity=opa,
            stroke_width=str_width,
            color=TEXT_SECONDARY,
            stroke_color=TEXT_PRIMARY
        )

        if tile_type == "info_vertical":
            pin = Pin(label=label).scale(pin_scale)
            name = Tex(
                capitalise_no_score(label),
                font_size=13,
                color=TEXT_PRIMARY,
            )
            matches_total = Tex(
                f"{matches_total} matches" if matches_total is not None else "-- matches",
                font_size=15,
                color=TEXT_SECONDARY,
            )
            winrate_total = Tex(
                f"{wr_total} \\%" if wr_total is not None else "-- matches",
                font_size=20,
                color=TEXT_PRIMARY,
            )
            pin.next_to(self.bg.get_corner(UL), DR, buff=0.1)
            name.next_to(self.bg.get_corner(DR), UL, aligned_edge=RIGHT, buff=0.1)
            winrate_total.next_to(pin, RIGHT, buff=0.1)
            matches_total.next_to(name, UP, aligned_edge=RIGHT, buff=0.1)
            content = Group(pin, name, matches_total, winrate_total)
            self.add(self.bg.set(fill_opacity=0), content)

        if tile_type == "info_horizontal":
            pin = Pin(label=label).scale(0.8 * pin_scale)
            name = Tex(
                capitalise_no_score(label),
                font_size=13,
                color=TEXT_PRIMARY,
            ).next_to(pin.get_corner(DOWN), DOWN, buff=0.1)
            content = Group(pin, name).next_to(
                self.bg.get_corner(DOWN), UP, buff=0
            )
            self.add(self.bg.set_opacity(0), content)

        elif tile_type == "diagonal":
            dot = Dot(
                point=self.bg.get_center(),
                radius=0.1,
                color=WHITE,
            )
            self.add(self.bg.set_opacity(0), dot)

        elif tile_type == "matrix":
            wr_hl = Tex(
                "--" if wr_high is None or wr_low is None else f"{wr_low:.0f}-{wr_high:.0f}\\%",
                font_size=13,
                color=TEXT_SECONDARY,
            )
            wr_text = Tex(
                "--" if wr is None else f"{wr:.0f} \\%",
                font_size=30,
                color=TEXT_PRIMARY,
            )
            wl_text = Tex(
                "--" if wins is None or losses is None else f"{wins}-{losses}",
                font_size=13,
                color=TEXT_SECONDARY,
            )
            no_data = Tex(
                "No data",
                font_size=25,
                color=TEXT_SECONDARY,
            ).move_to(self.bg.get_center())

            wr_text.move_to(self.bg.get_center())
            wr_hl.next_to(wr_text, UP, buff=0.2)
            wl_text.next_to(self.bg.get_corner(DOWN), UP, buff=0.1)
            content = Group(wr_text, wr_hl, wl_text)

            if wins == 0 and losses == 0:
                self.add(self.bg.set(stroke_color=TEXT_SECONDARY, fill_opacity=0.1), no_data)
            else:
                self.add(self.bg.set_color(CONFIDENCE_COLORS[confidence]), content)

        elif tile_type == "corner":
            self.add(self.bg)
