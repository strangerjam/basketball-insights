import streamlit as st

from utils.params import LocationName, OutcomeName, STATISTICS_TYPE, GRAPH_TYPE, format_graph_type_options, format_statistics_type_options, StatisticsTypeCode
from utils.games import one_team_game_set, combine_team_games
from utils.teams import define_team_options, format_team_options

from ui.graphs import make_team_statistics_graph

st.sidebar.selectbox(
    label='Base Team', key='team_base',
    options=define_team_options(),
    format_func=format_team_options
)

st.sidebar.selectbox(
    label='Matchup Team', key='team_matchup',
    options=define_team_options(),
    format_func=format_team_options,
    index=None,
    # disabled=st.session_state.team_1 is None,
    help='The second team can only be selected after the first team has been selected.'
)






# fetch data from NBA API for selected league and season
game_set = one_team_game_set(
    league=st.session_state.league,
    season_year=st.session_state.season_year
)
game_set = combine_team_games(df=game_set, keep_method=None)
# filter by selected team
game_set = game_set[game_set.TEAM_ID == st.session_state.team_base]
# filter by selected season type
# if st.session_state.season_type:
    # game_set = game_set[game_set.SEASON_CODE.isin(st.session_state.season_type)]


# st.write(
#     game_set
# )


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
    value=game_set.loc[game_set.GAME_OUTCOME == OutcomeName.LOSS.value, 'GAME_ID'].nunique()
)
cols_metrics[3].selectbox(
    label='Statistics Type', key='statistics_type',
    options=[
        key
        for key in STATISTICS_TYPE.keys()
        if key != StatisticsTypeCode.SCORE_DIFF.value
    ],
    format_func=format_statistics_type_options
)
cols_metrics[4].selectbox(
    label='Graph Type', key='graph_type',
    options=GRAPH_TYPE,
    format_func=format_graph_type_options
)
    

st.plotly_chart(
    make_team_statistics_graph(
        df=game_set,
        statistics_type=st.session_state.statistics_type,
        graph_type=st.session_state.graph_type,
        matchup_team=st.session_state.team_matchup
    )
)