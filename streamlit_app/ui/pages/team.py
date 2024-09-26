import streamlit as st

from utils.params import LocationName, OutcomeName, STATISTICS_TYPE, GRAPH_TYPE
from utils.games import one_team_game_set

from ui.graphs import make_team_statistics_graph

# fetch data from NBA API for selected league and season
game_set = one_team_game_set(
    league_code=st.session_state.league,
    season_year=st.session_state.season
)
# filter by selected team
game_set = game_set[game_set.TEAM_ID == st.session_state.team_base]
# filter by selected season type
if st.session_state.season_type:
    game_set = game_set[game_set.SEASON_CODE.isin(st.session_state.season_type)]



cols_metrics = st.columns([1, 1, 1, 3, 3])
cols_metrics[0].metric(
    label='Games Played',
    value=game_set.GAME_ID.nunique()
)
cols_metrics[1].metric(
    label='Wins',
    value=game_set.loc[game_set.GAME_OUTCOME == OutcomeName.WIN.value, 'GAME_ID'].nunique()
)
cols_metrics[2].metric(
    label='Losses',
    value=game_set.loc[game_set.GAME_OUTCOME == OutcomeName.WIN.value, 'GAME_ID'].nunique()
)
cols_metrics[3].selectbox(
    label='Statistics Type', key='statistics_type',
    options=STATISTICS_TYPE
)
cols_metrics[4].selectbox(
    label='Graph Type', key='graph_type',
    options=GRAPH_TYPE
)
    

st.plotly_chart(
    make_team_statistics_graph(
        df=game_set,
        statistics_type=st.session_state.statistics_type,
        graph_type=st.session_state.graph_type,
        matchup_team=st.session_state.team_matchup
    )
)

# st.write(
#     game_set
# )