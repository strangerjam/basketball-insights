from enum import Enum


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
    OUTCOME = 'MATCHUP_OUTCOME'
    PTS = 'PTS'
    FG2M = 'FG2M'
    FG3M = 'FG3M'
    REB = 'REB'
    AST = 'AST'

class StatisticsTypeName(Enum):
    OUTCOME = 'Outcome'
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