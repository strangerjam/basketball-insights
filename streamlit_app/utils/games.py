import streamlit as st

import pandas as pd
import re
from datetime import datetime, timedelta

from nba_api.stats.endpoints import leaguegamefinder, playbyplayv3

from utils.params import LocationName, OutcomeName, GAME_TIME
from utils.season import SEASON_TYPE
from utils.teams import get_league_teams, find_team_info_by_abbreviation, find_team_info_by_id

@st.cache_data(ttl=3600, show_spinner='Fetching data from NBA API...')
def find_games(league, season_year):
    '''
        Return data frame with the list of games for the selected league and season

        Parameters
        ----------
        league
        season_year

        Returns
        -------
        Result data frame

        SEASON_ID, GAME_DATE, MATCHUP
    '''

    # get data from nba api
    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguegamefinder.md
    try:
        games = leaguegamefinder.LeagueGameFinder(
            league_id_nullable=league,
            season_nullable=season_year,
        ).league_game_finder_results.get_data_frame()
    except ConnectionError:
        print(
            "Couldn't get the data from leaguegamefinder endpoint, league_game_finder_results dataset\n",
            "Parameters:\n",
            f"League Code: {league}\n",
            f"Season Year Code: {season_year}\n",
        )
    else:
        print("leaguegamefinder data received successfully")

    # leave useful columns only
    cols = ['SEASON_ID', 'GAME_DATE', 'GAME_ID', 'MATCHUP', 'TEAM_ID']
    games = games#[cols]

    # leave only home games
    # 'vs. ' - means the home game, otherwse ('@') - away game
    games = games.query('MATCHUP.str.contains("vs.")', engine='python')

    # sort games by game date
    games = games.sort_values(by='GAME_DATE', ascending=False)

    return games

@st.cache_data(ttl=3600, show_spinner='Fetching data from NBA API...')
def get_play_by_play_data(game, league):
    '''
        Return data frame with the play-by-play events for the selected game

        Parameters
        ----------
        game - selected row from the find_games() function results

        Returns
        -------
        Result data frame

        SEASON_ID, GAME_DATE, MATCHUP
    '''

    # get data from nba api
    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/playbyplayv3.md
    try:
        play_by_play = playbyplayv3.PlayByPlayV3(
            game_id=game.GAME_ID
        ).play_by_play.get_data_frame()
    except ConnectionError:
        print(
            "Couldn't get the data from playbyplayv3 endpoint, play_by_play dataset\n",
            "Parameters:\n",
            f"GAME_ID: {game.GAME_ID}\n"
        )
    else:
        print("playbyplayv3 data received successfully")

    home_team = find_team_info_by_abbreviation(league=league, abbreviation=game.MATCHUP[0][:3])
    road_team = find_team_info_by_abbreviation(league=league, abbreviation=game.MATCHUP[0][-3:])

    # fill data in teamId
    play_by_play['teamId'] = [id if id != 0 else None for id in play_by_play.teamId]
    # play_by_play['teamId'] = [
    #     play_by_play.teamId[i]
    #     if play_by_play.teamId[i] != 0
    #     else home_team['id']
    #         if home_team['nickname'].lower() in play_by_play.description[i].lower()
    #         else road_team['id']
    #             if road_team['nickname'].lower() in play_by_play.description[i].lower()
    #                 else 0
    #     for i in play_by_play.index
    # ]

    # fill data in teamTricode
    play_by_play['teamTricode'] = [code if code != '' else None for code in play_by_play.teamTricode]
    # play_by_play['teamTricode'] = [
    #     find_team_info_by_id(league=league, team_id=team_id, value='abbreviation')
    #     for team_id in play_by_play.teamId
    # ]

    # fill data in personId
    play_by_play['personId'] = [id if id != 0 else None for id in play_by_play.personId]

    # fill data in playerName
    play_by_play['playerName'] = [name if name != '' else None for name in play_by_play.playerName]
    play_by_play['playerNameI'] = [name if name != '' else None for name in play_by_play.playerNameI]

    # fill data in shotResult
    play_by_play['shotResult'] = [shot if shot != '' else None for shot in play_by_play.shotResult]

    # parse period time from the `clock` string
    play_by_play['periodTime'] = [
        datetime.strptime(x, 'PT%MM%S.%fS').replace(microsecond=0)
        for x in play_by_play.clock
    ]

    # define period and overtime length for the selected league
    period_length = GAME_TIME[league]['period']
    overtime_length = GAME_TIME[league]['overtime']

    play_by_play['periodTime'] = [
        datetime(1970, 1, 1)
            + timedelta(
                minutes=int(play_by_play.period[i] * period_length)
                    if play_by_play.period[i] <=4
                    else int((play_by_play.period[i] - 4) * overtime_length + 4 * period_length)
            )
            - timedelta(
                minutes=datetime.strptime(play_by_play.clock[i], 'PT%MM%S.%fS').time().minute,
                seconds=datetime.strptime(play_by_play.clock[i], 'PT%MM%S.%fS').time().second
            )
        for i in play_by_play.index
    ]

    # calc score diff
    play_by_play.scoreHome = [int(sc) if sc else None for sc in play_by_play.scoreHome]
    play_by_play.scoreAway = [int(sc) if sc else None for sc in play_by_play.scoreAway]
    play_by_play['scoreDiff'] = play_by_play.scoreHome - play_by_play.scoreAway

    # calc points
    play_by_play['points'] = [
        play_by_play.scoreHome[i] if play_by_play.teamId[i] == home_team['id']
        else play_by_play.scoreAway[i] if play_by_play.teamId[i] == road_team['id']
        else None
        for i in play_by_play.index
    ]

    # calc 2-point field goals
    play_by_play['fg2m'] = [
        1 if (play_by_play.actionType[i] == 'Made Shot') & ('3PT' not in play_by_play.description[i])
        else None
        for i in play_by_play.index
    ]
    play_by_play['fg2m'] = play_by_play.groupby('teamId').fg2m.cumsum()

    # calc 3-point field goals
    play_by_play['fg3m'] = [
        1 if (play_by_play.actionType[i] == 'Made Shot') & ('3PT' in play_by_play.description[i])
        else None
        for i in play_by_play.index
    ]
    play_by_play['fg3m'] = play_by_play.groupby('teamId').fg3m.cumsum()

    # calc revounds
    play_by_play['rebounds'] = [1 if play_by_play.actionType[i] == 'Rebound' else None for i in play_by_play.index]
    play_by_play['rebounds'] = play_by_play.groupby('teamId').rebounds.cumsum()

    # cals assists
    play_by_play['assists'] = [1 if re.search(r'\d AST', desc) else None for desc in play_by_play.description]
    play_by_play['assists'] = play_by_play.groupby('teamId').assists.cumsum()


    return play_by_play

@st.cache_data(ttl=3600, show_spinner='Fetching data from NBA API...')
def one_team_game_set(league=None, season_year=None, season_type=None, team_id=None):
    '''
        Return data frame with team's games info

        Parameters
        ----------
        league
            league code
        season_year
            season year
        season_type
            season type
        team_id
            team id

        Returns
        -------
        Result data frame

        SEASON_TYPE, GAME_DATE, GAME_ID,
        TEAM_ABBREVIATION, MATCHUP_TEAM_ID, MATCHUP_TEAM_ABBREVIATION, MATCHUP_LOCATION, MATCHUP_OUTCOME,
        PTS, FG2M, FG2A, FG3M, FG3A, REB, AST
    '''

    # get data from nba api
    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguegamefinder.md
    try:
        game_set = leaguegamefinder.LeagueGameFinder(
            league_id_nullable=league,
            season_nullable=season_year,
            season_type_nullable=season_type,
            team_id_nullable=team_id
        ).league_game_finder_results.get_data_frame()
    except ConnectionError:
        print(
            "Couldn't get the data from leaguegamefinder endpoint, league_game_finder_results dataset\n",
            "Parameters:\n",
            f"League Code: {league}\n",
            f"Season Year Code: {season_year}\n",
            f"Season Type Code: {season_type}\n",
            f"Team ID: {team_id}\n"
        )
    else:
        print("game_set data received successfully")

    # season type is defined with the first digit from season id
    game_set['SEASON_CODE'] = [x[:1] for x in game_set.SEASON_ID]
    game_set['SEASON_TYPE'] = [SEASON_TYPE[x[:1]] for x in game_set.SEASON_ID]

    # get list of teams from the same league to find matchups teams' info
    matchup_team = get_league_teams(league)

    # matchup team's abbreviation is define with the last 3 digits from MATCHUP record
    game_set['MATCHUP_TEAM_ABBREVIATION'] = [x[-3:] for x in game_set.MATCHUP]

    # leave games only with teams from the same league
    # for example: there may be out-of-the-league teams for Pre-Season league
    game_set = game_set[game_set.MATCHUP_TEAM_ABBREVIATION.isin(matchup_team.abbreviation.unique())]

    # define team id for each matchup team
    game_set['MATCHUP_TEAM_ID'] = [matchup_team.loc[matchup_team.abbreviation == abv, 'id'].values[0] for abv in game_set.MATCHUP_TEAM_ABBREVIATION]

    # define game location from MATCHUP record
    # 'vs. ' - means the home game, otherwse ('@') - away game
    game_set['GAME_LOCATION'] = [LocationName.HOME.value if 'vs.' in x else LocationName.ROAD.value for x in game_set.MATCHUP]
    
    # define game outcome from WL record 
    # 'W' - means the win, otherwise ('L') - loss
    game_set['GAME_OUTCOME'] = [OutcomeName.WIN.value if x == 'W' else OutcomeName.LOSS.value for x in game_set.WL]

    # number of 2-point FG is the difference between the total number of FG and the number of 3-point FG
    # same for attempts
    game_set['FG2M'] = [game_set.FGM[i] - game_set.FG3M[i] for i in game_set.index]
    game_set['FG2A'] = [game_set.FGA[i] - game_set.FG3A[i] for i in game_set.index]

    # define columns for output
    result_columns = [
        'SEASON_ID', 'SEASON_CODE', 'SEASON_TYPE', 'GAME_DATE', 'GAME_ID', 'GAME_LOCATION', 'GAME_OUTCOME',
        'TEAM_ID', 'TEAM_ABBREVIATION',
        'MATCHUP_TEAM_ID', 'MATCHUP_TEAM_ABBREVIATION',
        'PTS', 'FG2M', 'FG2A', 'FG3M', 'FG3A', 'REB', 'AST'
    ]
    # select data with defined columns only
    game_set = game_set[result_columns]

    return game_set

# source: https://github.com/swar/nba_api/blob/master/docs/examples/Finding%20Games.ipynb
def combine_team_games(df, keep_method='home'):
    '''
        Combine a TEAM_ID-GAME_ID unique table into rows by game. Slow.

        Parameters
        ----------
        df : Input DataFrame.
        keep_method : {'home', 'road', 'winner', 'loser', ``None``}, default 'home'
            - 'home' : Keep rows where TEAM_A is the home team.
            - 'road' : Keep rows where TEAM_A is the road team.
            - 'winner' : Keep rows where TEAM_A is the losing team.
            - 'loser' : Keep rows where TEAM_A is the winning team.
            - ``None`` : Keep all rows. Will result in an output DataFrame the same
                length as the input DataFrame.
                
        Returns
        -------
        result : DataFrame
    '''
    # Join every row to all others with the same game ID.
    joined = pd.merge(
        left=df,
        right=df,
        suffixes=['', '_RIGHT'],
        on=['SEASON_ID', 'GAME_ID', 'GAME_DATE']
    )

    # Filter out any row that is joined to itself.
    result = joined[joined.TEAM_ID != joined.TEAM_ID_RIGHT]

    # remove duplicated columns
    result = result[result.columns[['_RIGHT' not in col for col in result.columns]]]
    
    # Take action based on the keep_method flag.
    if keep_method is None:
        # Return all the rows.
        pass
    elif keep_method.lower() == 'home':
        # Keep rows where TEAM_A is the home team.
        result = result[result.GAME_LOCATION == LocationName.HOME.value]
    elif keep_method.lower() == 'road':
        # Keep rows where TEAM_A is the away team.
        result = result[result.GAME_LOCATION == LocationName.ROAD.value]
    elif keep_method.lower() == 'winner':
        result = result[result.GAME_OUTCOME == OutcomeName.WIN.value]
    elif keep_method.lower() == 'loser':
        result = result[result.GAME_OUTCOME == OutcomeName.LOSS.value]
    else:
        raise ValueError(f'Invalid keep_method: {keep_method}')
    
    return result