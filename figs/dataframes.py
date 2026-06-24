from mtga_viz.core.database_manipulation import *
from mtga_viz.core.stats import *


CURRENT_ANALYSIS = '../data/win_loss_mtg_ds.numbers'

df = numbers_to_df(path=CURRENT_ANALYSIS)

summary_archetype = get_archetype_summary(df, granularity=9)
summary_deck = get_deck_summary(df, 'Energy', granularity=1)
summary_tricks = get_tricks(df)
