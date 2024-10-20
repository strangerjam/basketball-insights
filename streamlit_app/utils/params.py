from enum import Enum

from utils.league import LeagueCode

class LocationName(Enum):
    HOME = 'Home'
    ROAD = 'Road'

class LocationCode(Enum):
    HOME = 'home'
    ROAD = 'road'

class OutcomeName(Enum):
    WIN = 'Win'
    LOSS = 'Loss'

class OutcomeCode(Enum):
    WIN = 'win'
    LOSS = 'loss'

class StatisticsTypeCode(Enum):
    SCORE_DIFF = 'SCORE_DIFF'
    # OUTCOME = 'OUTCOME'
    PTS = 'PTS'
    FG2M = 'FG2M'
    FG3M = 'FG3M'
    REB = 'REB'
    AST = 'AST'

class StatisticsTypeName(Enum):
    SCORE_DIFF = 'Score Difference'
    # OUTCOME = 'Outcome'
    PTS = 'Total Points'
    FG2M = '2-Point Field Goals'
    FG3M = '3-Point Field Goals'
    REB = 'Rebounds'
    AST = 'Assists'

class GraphTypeCode(Enum):
    BAR = 'BAR'
    BOX = 'BOX'

class GraphTypeName(Enum):
    BAR = 'Bar Chart'
    BOX = 'Box Plot'

LOCATION = {
    LocationCode.HOME.value : LocationName.HOME.value,
    LocationCode.ROAD.value : LocationName.ROAD.value
}

OUTCOME = {
    OutcomeCode.WIN.value : OutcomeName.WIN.value,
    OutcomeCode.LOSS.value : OutcomeName.LOSS.value
}

STATISTICS_TYPE = {
    StatisticsTypeCode.SCORE_DIFF.value : StatisticsTypeName.SCORE_DIFF.value,
    # StatisticsTypeCode.OUTCOME.value : StatisticsTypeName.OUTCOME.value,
    StatisticsTypeCode.PTS.value : StatisticsTypeName.PTS.value,
    StatisticsTypeCode.FG2M.value : StatisticsTypeName.FG2M.value,
    StatisticsTypeCode.FG3M.value : StatisticsTypeName.FG3M.value,
    StatisticsTypeCode.REB.value : StatisticsTypeName.REB.value,
    StatisticsTypeCode.AST.value : StatisticsTypeName.AST.value
}

TIMEFRAME = {
    'GAME' : 'Game',
    'PERIOD' : 'Period'
    # 'MINUTE' : 'Minute'
}

GRAPH_TYPE = {
    GraphTypeCode.BAR.value : GraphTypeName.BAR.value,
    GraphTypeCode.BOX.value : GraphTypeName.BOX.value
}

# length of the standard period and overtime in minutes for different leagues
GAME_TIME = {
    LeagueCode.NBA.value : {
        'period' : 12,
        'overtime' : 5
    },
    LeagueCode.WNBA.value : {
        'period' : 10,
        'overtime' : 5
    }
}


def format_statistics_type_options(key):
    '''
        Function is used for the Streamlit's input to modify the display of selected options
    '''

    return STATISTICS_TYPE[key]


def format_graph_type_options(key):
    '''
        Function is used for the Streamlit's input to modify the display of selected options
    '''

    return GRAPH_TYPE[key]