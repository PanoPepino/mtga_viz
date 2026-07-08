from manim import *
from mtga_viz.viz.objects.tile import Tile


class MatchupMatrix(Group):
    """Reusable matchup matrix plot built from saved matrix dictionaries."""

    def __init__(
        self,
        matrix_dict: dict,
        wr_dict: dict | None = None,
        buff: float = 0.1,
        frame_height: float | None = None,
        **kwargs,
    ):
        """Create matchup matrix object.

        Args:
            matrix_dict: Dictionary with deck order and matchup lookup data.
            wr_dict: Optional dictionary with overall deck matches and win rates.
            buff: Spacing between tiles.
            frame_height: Optional target height for whole plot.
            **kwargs: Extra keyword arguments passed to Group.
        """
        super().__init__(**kwargs)

        labels = matrix_dict["deck_order_rows"]
        lookup = matrix_dict["matchup_lookup"]
        n = len(labels)

        matches_played_map = {}
        winrates_map = {}
        if wr_dict is not None:
            matches_played_map = dict(zip(wr_dict["labels"], wr_dict["matches_played"]))
            winrates_map = dict(zip(wr_dict["labels"], wr_dict["wr"]))

        top_info = Group()
        for lab in labels:
            top_info.add(
                Tile(
                    tile_type="info_horizontal",
                    label=lab,
                )
            )
        top_info.arrange(RIGHT, buff=buff)

        left_info = Group()
        for lab in labels:
            left_info.add(
                Tile(
                    tile_type="info_vertical",
                    label=lab,
                    matches_total=matches_played_map.get(lab),
                    wr_total=winrates_map.get(lab),
                    opa=0.3
                )
            )
        left_info.arrange(DOWN, buff=buff)

        body = Group()
        for i in range(n):
            row = Group()
            user_deck = labels[i]

            for j in range(n):
                oppo_deck = labels[j]

                if user_deck == oppo_deck:
                    tile = Tile(
                        tile_type="diagonal",
                        label=user_deck,
                    )
                else:
                    cell = lookup.get(user_deck, {}).get(oppo_deck, {
                        "matches": 0,
                        "wins": 0,
                        "losses": 0,
                        "wr": 0,
                        "wr_high": 0,
                        "wr_low": 0,
                        "confidence": "none",
                    })
                    tile = Tile(
                        tile_type="matrix",
                        label=user_deck,
                        opa=0.5,
                        wr=cell["wr"],
                        wins=cell["wins"],
                        losses=cell["losses"],
                        wr_high=cell["wr_high"],
                        wr_low=cell["wr_low"],
                        confidence=cell["confidence"],
                    )
                row.add(tile)

            row.arrange(RIGHT, buff=buff)
            body.add(row)

        body.arrange(DOWN, buff=buff, aligned_edge=LEFT)

        body.next_to(left_info, RIGHT, buff=buff, aligned_edge=UP)
        top_info.next_to(body, UP, buff=buff, aligned_edge=LEFT)

        self.top_info = top_info
        self.left_info = left_info
        self.body = body
        self.matrix_plot = Group(top_info, left_info, body)

        if frame_height is not None:
            self.matrix_plot.scale_to_fit_height(frame_height)

        self.add(self.matrix_plot)
