import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd
from datetime import datetime, timedelta

from utils.params import STATISTICS_TYPE, StatisticsTypeCode, OutcomeName, GraphTypeCode

# set default template for all graphs
pio.templates.default = "plotly_white"

# define graph parameters
COLOR_WIN = 'green'
COLOR_LOSS = 'red'
COLOR_BACKGROUND = 'white'
COLOR_FONT = 'darkslategray'
COLOR_HIGHLIGHT = 'orangered'
COLOR_PRIMARY = 'blue'
COLOR_HLINE = 'magenta'
COLOR_HLINE_FONT = 'white'


def make_team_statistics_graph_outcome(df, matchup_team):
    '''
        Return figure
    '''
    
    # exclude records with matchup team if exists
    matchup_df = df if matchup_team is None else df[df.MATCHUP_TEAM_ID == matchup_team]

    # initial figure object
    outcome_graph = go.Figure()

    # add graph component for WIN games
    outcome_graph.add_indicator(
        mode='number',
        domain={'row': 0, 'column': 0},
        value=matchup_df.loc[matchup_df.GAME_OUTCOME == OutcomeName.WIN.value, 'GAME_DATE'].nunique(),
        title={
            'text': f'{OutcomeName.WIN.value}',
            'font': {
                'color': COLOR_WIN,
                'textcase': 'upper',
                'weight': 600
            }
        }
    )

    # add graph component for LOSS games
    outcome_graph.add_indicator(
        mode='number',
        domain={'row': 0, 'column': 1},
        value=matchup_df.loc[matchup_df.GAME_OUTCOME == OutcomeName.LOSS.value, 'GAME_DATE'].nunique(),
        title={
            'text': f'{OutcomeName.LOSS.value}',
            'font': {
                'color': COLOR_LOSS,
                'textcase': 'upper',
                'weight': 600
            }
        }
    )

    # add graph component with list of games
    outcome_graph.add_table(
        domain={'row': 1, 'column': 2},
        header=dict(
            values=[
                '<b>Season Type</b>', '<b>Matchup</b>', '<b>Game Date</b>',
                '<b>Location</b>', '<b>Outcome</b>', '<b>Points</b>'
            ],
            fill_color=COLOR_BACKGROUND,
            font=dict(
                color=COLOR_FONT,
                size=14
            )
        ),
        cells=dict(
            values=[
                matchup_df.SEASON_TYPE, matchup_df.MATCHUP_TEAM_ABBREVIATION, matchup_df.GAME_DATE,
                matchup_df.GAME_LOCATION, matchup_df.GAME_OUTCOME, matchup_df.PTS
            ],
            fill_color=COLOR_BACKGROUND,
            font=dict(
                color=COLOR_FONT,
                size=12
            )
        )
    )

    # set layout for graphs
    outcome_graph.update_layout(
        grid = {'rows': 2, 'columns': 2}
    )

    return outcome_graph

def make_team_statistics_graph_type_bar(df, recent_game, statistics_type, matchup_team):
    '''
        Return figure
    '''
    
    # define matchup team abbreviation in 2 steps
    #   1. select game records with matchup teams
    #   2. return unique abbreviation if at least one record exists
    matchup_team_abv = df.loc[df.MATCHUP_TEAM_ID == matchup_team, 'MATCHUP_TEAM_ABBREVIATION']
    matchup_team_abv = None if len(matchup_team_abv) == 0 else matchup_team_abv.unique()[0]

    # define colors
    colors = {matchup_team_abv : COLOR_HIGHLIGHT}
    default_color = COLOR_PRIMARY

    # create figure
    bar_chart = px.bar(
        data_frame=df,
        x='GAME_DATE', y=statistics_type,
        color='MATCHUP_TEAM_ABBREVIATION',
        color_discrete_map={t: colors.get(t, default_color) for t in df.MATCHUP_TEAM_ABBREVIATION.unique()},
        custom_data=['SEASON_TYPE', 'MATCHUP_TEAM_ABBREVIATION', 'GAME_LOCATION', 'GAME_OUTCOME']
    )

    # add hover text
    bar_chart.update_traces(
        hovertemplate=
            '<b>%{x|%b %d, %Y}</b><br>' +
            '<b>%{customdata[0]}</b><br><br>' +
            'Matchup: <b>%{customdata[1]}</b><br>' +
            'Location: <b>%{customdata[2]}</b><br>' +
            'Outcome: <b>%{customdata[3]}</b><br><br>' +
            STATISTICS_TYPE[statistics_type] + ': <b>%{y}</b>' +
            '<extra></extra>'
    )

    # add last game as a line if it is today or if it was yesterday
    if recent_game is not None:
        # generade date range for x-axis
        date_range = pd.date_range(df.GAME_DATE.min(), df.GAME_DATE.max(), freq='d')

        # add line
        bar_chart.add_scatter(
            x=date_range,
            y=[recent_game[statistics_type]]*len(date_range),
            mode='lines',
            name='Recent Game',
            marker=dict(
                color=COLOR_HLINE
            ),
            hovertemplate=
                '<b>Recent Game</b><br><br>' +
                '<b>' + datetime.strptime(recent_game.GAME_DATE, '%Y-%m-%d').strftime('%b %d, %Y') + '</b><br>' +
                '<b>' + recent_game.SEASON_TYPE + '</b><br><br>' +
                'Matchup: <b>' + recent_game.MATCHUP_TEAM_ABBREVIATION + '</b><br>' +
                'Location: <b>' + recent_game.GAME_LOCATION + '</b><br>' +
                'Outcome: <b>' + recent_game.GAME_OUTCOME + '</b><br><br>' +
                STATISTICS_TYPE[statistics_type] + ': <b>%{y}</b>' +
                '<extra></extra>'
        )

    return bar_chart

def make_team_statistics_graph_type_box(df, recent_game, statistics_type, matchup_team):
    '''
        Return figure
    '''
    
    # define colors
    colors = {matchup_team : COLOR_HIGHLIGHT}
    default_color = COLOR_PRIMARY

    # create figure
    box_plot = px.strip(
        data_frame=df,
        y=statistics_type,
        color='MATCHUP_TEAM_ID',
        color_discrete_map={t: colors.get(t, default_color) for t in df.MATCHUP_TEAM_ID.unique()},
        custom_data=['GAME_DATE', 'SEASON_TYPE', 'MATCHUP_TEAM_ABBREVIATION', 'GAME_LOCATION', 'GAME_OUTCOME']
    )

    # add hover text
    box_plot.update_traces(
        hovertemplate=
            '<b>%{customdata[0]|%b %d, %Y}</b><br>' +
            '<b>%{customdata[1]}</b><br><br>' +
            'Matchup: <b>%{customdata[2]}</b><br>' +
            'Location: <b>%{customdata[3]}</b><br>' +
            'Outcome: <b>%{customdata[4]}</b><br><br>' +
            STATISTICS_TYPE[statistics_type] + ': <b>%{y}</b>' +
            '<extra></extra>'
    )
    
    # add graph component
    box_plot.add_trace(
        go.Box(
            y=df[statistics_type],
            boxmean='sd',
            marker_color=default_color,
            width=1,
            name='',
            hoverinfo='y'
        )
    )

    # add last game as a line if it is today or if it was yesterday
    if recent_game is not None:
        box_plot.add_hline(
            y=recent_game[statistics_type],
            line=dict(
                color=COLOR_HLINE
            ),
            annotation_position='bottom right',
            annotation_text='<b>-> Recent Game</b>',
            annotation=dict(
                font_size=14,
                font_color=COLOR_HLINE,
                hovertext=
                    '<b>' + datetime.strptime(recent_game.GAME_DATE, '%Y-%m-%d').strftime('%b %d, %Y') + '</b><br>' +
                    '<b>' + recent_game.SEASON_TYPE + '</b><br><br>' +
                    'Matchup: <b>' + recent_game.MATCHUP_TEAM_ABBREVIATION + '</b><br>' +
                    'Location: <b>' + recent_game.GAME_LOCATION + '</b><br>' +
                    'Outcome: <b>' + recent_game.GAME_OUTCOME + '</b><br><br>' +
                    STATISTICS_TYPE[statistics_type] + ': <b>' + str(recent_game[statistics_type]) + '</b>',
                hoverlabel=dict(
                    bgcolor=COLOR_HLINE,
                    font_color=COLOR_HLINE_FONT,
                    font_size=13
                )
            )
        )

    return box_plot

def make_team_statistics_graph(df, statistics_type, graph_type, matchup_team):
    '''
        Return figure

        Parameters
        ----------
        data
            input data with team information: games and statistics
        statistics_type
            total points, 2-point field goals and so on
        graph_type
            bar chart, box plot, etc.
        matchup team
            can be None

        Returns
        -------
        Result figure
    '''

    # sort games be game date starting from the last game
    df = df.sort_values(by='GAME_DATE', ascending=False)

    # find last game record if it exists
    if len(df) > 0:
        recent_game = df.iloc[0, ]

        # define if last game is today 
        is_recent_game_today = recent_game.GAME_DATE == datetime.today().strftime('%Y-%m-%d')
        
        # define if last game was yesterday
        is_recent_game_yesterday = recent_game.GAME_DATE == (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

        # exclude last game from df for graphs if it is today or if it was yesterday
        # otherwise - set recent_game to None to use it in make_*_graph functions
        if is_recent_game_today | is_recent_game_yesterday:
            df = df[df.GAME_DATE != recent_game.GAME_DATE]
        else:
            recent_game = None
    else:
        recent_game = None

    # make graph depends on UI's inputs
    if statistics_type == StatisticsTypeCode.OUTCOME.value:
        fig = make_team_statistics_graph_outcome(
            df=df,
            matchup_team=matchup_team
        )
    elif graph_type == GraphTypeCode.BOX.value:
        fig = make_team_statistics_graph_type_box(
            df=df, recent_game=recent_game,
            statistics_type=statistics_type, matchup_team=matchup_team
        )
    elif graph_type == GraphTypeCode.BAR.value:
        fig = make_team_statistics_graph_type_bar(
            df=df, recent_game=recent_game,
            statistics_type=statistics_type, matchup_team=matchup_team
        )

    # set y-axis to 0
    fig.update_yaxes(rangemode='tozero')

    # hide legend and title
    fig.update_layout(
        showlegend=False,
        xaxis_title=None, yaxis_title=None,
        height=600
    )

    return fig