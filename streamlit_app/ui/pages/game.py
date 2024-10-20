import streamlit as st

from datetime import datetime

from utils.params import STATISTICS_TYPE, StatisticsTypeCode, format_statistics_type_options
from utils.league import LEAGUE, LeagueCode
from utils.season import SEASON_YEAR, SEASON_TYPE, SeasonTypeCode
from utils.teams import get_league_teams
from utils.games import find_games, get_play_by_play_data

from ui.graphs import make_game_statistics_graph

games = find_games(
    league=st.session_state.league,
    season_year=st.session_state.season_year
)

with st.sidebar:
    st.date_input(
        label='Game Date', key='game_date',
        min_value=datetime.strptime(games.GAME_DATE.min(), '%Y-%m-%d'),
        max_value=datetime.strptime(games.GAME_DATE.max(), '%Y-%m-%d'),
        value=datetime.strptime(games.GAME_DATE.max(), '%Y-%m-%d'),
        format='YYYY-MM-DD'
    )

    st.selectbox(
        label='Matchup', key='matchup',
        options=games.loc[games.GAME_DATE == str(st.session_state.game_date), 'MATCHUP']
    )

cols = st.columns([3, 9])

if st.session_state.matchup:
    selected_game = games[(games.GAME_DATE == str(st.session_state.game_date)) & (games.MATCHUP == st.session_state.matchup)]
    selected_game = selected_game.reset_index(drop=True)

    selected_game_season_type_id = selected_game.SEASON_ID[0][:1]
    selected_game_id = selected_game.GAME_ID[0]

    play_by_play = get_play_by_play_data(
        game=selected_game,
        league=st.session_state.league
    )

    st.write(
        f'Final Score {play_by_play.iloc[-1].scoreHome.astype(int)} : {play_by_play.iloc[-1].scoreAway.astype(int)}'
    )

    st.radio(
        label='Statistics Type', key='statistics_type',
        options=STATISTICS_TYPE.keys(),
        horizontal=True, label_visibility='collapsed',
        format_func=format_statistics_type_options
    )

    game_graph = make_game_statistics_graph(
        df=play_by_play,
        statistics_type=st.session_state.statistics_type,
        league=st.session_state.league,
        matchup=selected_game.MATCHUP[0]
    )

    st.plotly_chart(
        game_graph
    )

    st.write(
        selected_game
    )

    st.write(
        play_by_play#.query('actionType in ("Made Shot", "Free Throw")')
    )