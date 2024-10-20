import urllib

from teams import get_league_teams
from league import LeagueCode

# parse teams logo
for league in LeagueCode:
    # parse league logos
    if league.value == '00':
        # source_path = 'https://logocdn.com/nba/'
        source_path = 'https://cdn.nba.com/logos/leagues/logo-nba.svg'
    elif league.value == '10':
        source_path = 'https://cdn.nba.com/logos/leagues/logo-wnba.svg'

    target_path = 'streamlit_app/static/league_logo/' + league.value + '.svg'
    urllib.request.urlretrieve(source_path, target_path)

    # parse league logos
    teams = get_league_teams(league=league.value)

    for team in teams.id:
        if league.value == '00':
            source_path = 'https://cdn.nba.com/logos/nba/' + str(team) + '/primary/L/logo.svg'
        elif league.value == '10':
            source_path = 'https://cdn.nba.com/logos/wnba/' + str(team) + '/primary/L/logo.svg'

        target_path = 'streamlit_app/static/league_team_logo/' + league.value + '/' + str(team) + '.svg'
        urllib.request.urlretrieve(source_path, target_path)