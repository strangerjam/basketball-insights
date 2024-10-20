from enum import Enum

from nba_api.stats.endpoints import leaguestandingsv3

class LeagueName(Enum):
    NBA = 'NBA'
    WNBA = 'WNBA'
    # ABA = 'ABA'
    # GLEAGUE = 'G-League'

class LeagueCode(Enum):
    NBA = '00'
    WNBA = '10'
    # ABA = '01'
    # GLEAGUE = '20'


LEAGUE = {
    LeagueCode.NBA.value : LeagueName.NBA.value,
    LeagueCode.WNBA.value : LeagueName.WNBA.value
}

def format_league_options(key):
    '''
        Function is used for the Streamlit's input to modify the display of selected options
    '''

    return LEAGUE[key]