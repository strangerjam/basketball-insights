import streamlit as st

import pandas as pd

from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster

from utils.league import LeagueCode


# get NBA teams data from nba api
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/static/teams.md
def get_nba_teams():
    try:
        result = teams.get_teams()
        result = pd.json_normalize(result)
    except ConnectionError:
        print('Couldn`t get NBA teams')
    else:
        print('NBA teams data received successfully')
        return result

# get WNBA teams data from nba api
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/static/teams.md
def get_wnba_teams():
    try:
        result = teams.get_wnba_teams()
        result = pd.json_normalize(result)
    except ConnectionError:
        print('Couldn`t get NBA teams')
    else:
        print('WNBA teams data received successfully')
        return result

# get teams for the selected league
@st.cache_data(ttl=3600, show_spinner=False)
def get_league_teams(league):
    if league == LeagueCode.NBA.value:
        return get_nba_teams()
    elif league == LeagueCode.WNBA.value:
        return get_wnba_teams()
    else:
        print('Unknown league is selected')

# get team's full name based on team id and league
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/static/teams.md
@st.cache_data(ttl=3600, show_spinner=False)
def find_team_info_by_id(league, team_id, value=None):
    if team_id:
        if league == LeagueCode.NBA.value:
            try:
                result = teams.find_team_name_by_id(team_id=team_id)
                result = result[value] if value else result
            except ConnectionError:
                print(f'Couldn`t fine team info {value} by id {team_id} (NBA)')
            else:
                print(f'Team info (NBA) by id {team_id} was found successfully')
                return result
        elif league == LeagueCode.WNBA.value:
            try:
                result = teams.find_wnba_team_name_by_id(team_id=team_id)
                result = result[value] if value else result
            except ConnectionError:
                print(f'Couldn`t fine team info {value} by id {team_id} (WNBA)')
            else:
                print(f'Team info {value} (WNBA) by id {team_id} was found successfully')
                return result
        else:
            print(f'Unknown league is selected: {league}')
    else:
        print('None team was selected')

# get team's full name based on team id and league
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/static/teams.md
@st.cache_data(ttl=3600, show_spinner=False)
def find_team_info_by_abbreviation(league, abbreviation, value=None):
    if abbreviation:
        if league == LeagueCode.NBA.value:
            try:
                result = teams.find_team_by_abbreviation(abbreviation=abbreviation)
                result = result[value] if value else result
            except ConnectionError:
                print(f'Couldn`t fine team info {value} by abbreviation {abbreviation} (NBA)')
            else:
                print(f'Team info {value} (NBA) by abbreviation {abbreviation} was found successfully')
                return result
        elif league == LeagueCode.WNBA.value:
            try:
                result = teams.find_wnba_team_by_abbreviation(abbreviation=abbreviation)
                result = result[value] if value else result
            except ConnectionError:
                print(f'Couldn`t fine team name by abbreviation {abbreviation} (WNBA)')
            else:
                print(f'Team info {value} (WNBA) by abbreviation {abbreviation} was found successfully')
                return result
        else:
            print(f'Unknown league is selected: {league}')
    else:
        print('None team was selected')

def team_head_coach(team_id, season_year):
    '''
        Return one row data frame with head coach info

        Parameters
        ----------
        team_id
        season_year

        Returns
        -------
        Result data frame
    '''

    # get data from nba api
    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/commonteamroster.md
    try:
        coaches = commonteamroster.CommonTeamRoster(team_id=team_id, season=season_year).coaches.get_data_frame()
    except ConnectionError:
        print(
            'Couldn`t get the data from commonteamroster endpoint, coaches dataset\n',
            'Parameters:\n',
            f'Season Year Code: {season_year}\n',
            f'Team ID: {team_id}\n'
        )
    else:
        print('Coaches data received successfully')
        # select info for head coach only
        head_coach = coaches.loc[coaches.COACH_TYPE == 'Head Coach', ]

        return head_coach

def team_roster(league_id, team_id, season_year):
    '''
        Return data frame with team roaster for the season

        Parameters
        ----------
        league_id
        team_id
        season_year

        Returns
        -------
        Result data frame
    '''

    # get data from nba api
    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/commonteamroster.md
    try:
        roster = commonteamroster.CommonTeamRoster(
            league_id_nullable=league_id,
            team_id=team_id,
            season=season_year
        ).common_team_roster.get_data_frame()
    except ConnectionError:
        print(
            'Couldn`t get the data from commonteamroster endpoint, common_team_roster dataset\n',
            'Parameters:\n',
            f'Season Year Code: {season_year}\n',
            f'Team ID: {team_id}\n'
        )
    else:
        print('Roster data received successfully')
        return roster
    
def define_team_options():
    '''
        Define team option to select
    '''
    league = st.session_state.league

    teams = get_league_teams(league).sort_values(by='full_name')
    options = teams.id

    return options

def format_team_options(team_id):
    '''
        Define the selected league from UI and calls the function to define selected team's full name
    '''
    league = st.session_state.league
    
    return find_team_info_by_id(league=league, team_id=team_id, value='full_name')