import streamlit as st

import pandas as pd

from nba_api.stats.endpoints import leaguegamefinder

from utils.params import LocationName, OutcomeName
from utils.season import SEASON_TYPE
from utils.teams import get_league_teams

@st.cache_data(ttl=3600, show_spinner='Fetching data from NBA API...')
def one_team_game_set(league_code=None, season_year=None, season_type=None, team_id=None):
    '''
        Return data frame with team's games info

        Parameters
        ----------
        league_code
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
            league_id_nullable=league_code,
            season_nullable=season_year,
            season_type_nullable=season_type,
            team_id_nullable=team_id
        ).league_game_finder_results.get_data_frame()
    except ConnectionError:
        print(
            "Couldn't get the data from leaguegamefinder endpoint, league_game_finder_results dataset\n",
            "Parameters:\n",
            f"League Code: {league_code}\n",
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
    matchup_team = get_league_teams(league_code)

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