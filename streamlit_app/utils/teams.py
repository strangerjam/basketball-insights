import sys
import pandas as pd

from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster

from utils.league import LeagueCode


# get NBA teams data from nba api
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/static/teams.md
def try_get_teams():
    try:
        result = teams.get_teams()
    except ConnectionError:
        print("Couldn't get NBA teams")
        sys.exit(1)
    else:
        print("NBA teams data received successfully")
        return result

# get WNBA teams data from nba api
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/static/teams.md
def try_get_wnba_teams():
    try:
        result = teams.get_wnba_teams()
    except ConnectionError:
        print("Couldn't get NBA teams")
        sys.exit(1)
    else:
        print("WNBA teams data received successfully")
        return result

# define teams for each league
TEAMS = {
    LeagueCode.NBA.value : pd.json_normalize(try_get_teams()),
    LeagueCode.WNBA.value : pd.json_normalize(try_get_wnba_teams())
}


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
            "Couldn't get the data from commonteamroster endpoint, coaches dataset\n",
            "Parameters:\n",
            f"Season Year Code: {season_year}\n",
            f"Team ID: {team_id}\n"
        )
        sys.exit(1)
    else:
        print("coaches data received successfully")
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
            "Couldn't get the data from commonteamroster endpoint, common_team_roster dataset\n",
            "Parameters:\n",
            f"Season Year Code: {season_year}\n",
            f"Team ID: {team_id}\n"
        )
        sys.exit(1)
    else:
        print("roster data received successfully")
        return roster
