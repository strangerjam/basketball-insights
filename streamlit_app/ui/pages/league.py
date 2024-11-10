import streamlit as st

from ui.graphs import make_league_rating_graph

from utils.teams import get_team_rating

team_rating = get_team_rating(
    league=st.session_state.league,
    season=st.session_state.season_year
)

st.plotly_chart(
    make_league_rating_graph(df=team_rating, league=st.session_state.league),
    config={'displayModeBar': False}
)

# st.write(
#     team_rating
# )