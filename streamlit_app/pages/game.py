import streamlit as st

from utils.league import LEAGUE, LeagueCode, league_value_by_key
from utils.season import SEASON_YEAR, SEASON_TYPE, SeasonTypeCode, season_type_value_by_key
from utils.teams import get_league_teams
from utils.games import one_team_game_set




# col_tables = st.columns([1,1])

# with st.container():
#     col_tables[0].dataframe(
#         get_league_teams(st.session_state.league)
#     )

#     col_tables[1].dataframe(
#         one_team_game_set(
#             league_code=st.session_state.league,
#             season_year=st.session_state.season,
#             # season_type=st.session_state.season_type,
#             team_id=1610612738 if st.session_state.league == '00' else 1611661313
#         )
#     )

