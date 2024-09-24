import streamlit as st

from utils.league import LEAGUE, league_value_by_key
from utils.season import SEASON_YEAR, SEASON_TYPE, SeasonTypeCode, season_type_value_by_key
from utils.teams import TEAMS
from utils.games import one_team_game_set

st.set_page_config(
    page_title='Game',
    layout='wide',
    initial_sidebar_state='expanded'
)


left_3, middle_3, right_3 = st.columns(3)
left_2, right_2 = st.columns(2)

with st.container():
    left_3.selectbox(
        label='League', key='league',
        options=LEAGUE,
        format_func=league_value_by_key
    )

    middle_3.selectbox(
        label='Season', key='season',
        options=SEASON_YEAR[st.session_state.league],
    )

    right_3.multiselect(
        label='Season Type', key='season_type',
        options=SEASON_TYPE,
        default=[SeasonTypeCode.PLAYOFF.value, SeasonTypeCode.REGULAR.value],
        format_func=season_type_value_by_key,
        help='No selected season type means all season types.'
    )

with st.container():
    left_2.dataframe(
        TEAMS[st.session_state.league]
    )

    right_2.dataframe(
        one_team_game_set(
            league_code=st.session_state.league,
            season_year=st.session_state.season,
            # season_type=st.session_state.season_type,
            team_id=1610612738 if st.session_state.league == '00' else 1611661313
        )
    )