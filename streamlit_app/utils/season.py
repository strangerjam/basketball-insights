from enum import Enum

from nba_api.stats.library.parameters import Season, WnbaSeason

from utils.league import LeagueCode


class SeasonTypeName(Enum):
    PRE_SEASON = 'Pre-Season'
    REGULAR = 'Regular Season'
    ALL_STAR = 'All-Star'
    PLAYOFF = 'Playoffs'
    PLAY_IN = 'Play-In'
    IN_SEASON = 'In-Season'

class SeasonTypeCode(Enum):
    PRE_SEASON = '1'
    REGULAR = '2'
    ALL_STAR = '3'
    PLAYOFF = '4'
    PLAY_IN = '5'
    IN_SEASON = '6'


SEASON_TYPE = {
    SeasonTypeCode.PLAYOFF.value : SeasonTypeName.PLAYOFF.value,
    SeasonTypeCode.PLAY_IN.value : SeasonTypeName.PLAY_IN.value,
    SeasonTypeCode.REGULAR.value : SeasonTypeName.REGULAR.value,
    SeasonTypeCode.IN_SEASON.value : SeasonTypeName.IN_SEASON.value,
    SeasonTypeCode.PRE_SEASON.value : SeasonTypeName.PRE_SEASON.value,
    SeasonTypeCode.ALL_STAR.value : SeasonTypeName.ALL_STAR.value
}

SEASON_YEAR = {
    LeagueCode.NBA.value : [
        Season.current_season,
        Season.previous_season
    ],
    LeagueCode.WNBA.value : [
        WnbaSeason.current_season,
        WnbaSeason.previous_season
    ]
}

def season_type_value_by_key(key):
    '''
        Function is used for the Streamlit's input to modify the display of selected options
    '''
    
    return SEASON_TYPE[key]