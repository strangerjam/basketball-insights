import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd
import numpy as np
from math import floor, ceil
from datetime import datetime, timedelta

from PIL import Image

from utils.params import STATISTICS_TYPE, StatisticsTypeCode, OutcomeName, GraphTypeCode
from utils.teams import find_team_info_by_id, find_team_info_by_abbreviation

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
        
    # print(df.iloc[0, ])

    # make graph depends on UI's inputs
    # if statistics_type == StatisticsTypeCode.OUTCOME.value:
    #     fig = make_team_statistics_graph_outcome(
    #         df=df,
    #         matchup_team=matchup_team
    #     )
    if graph_type == GraphTypeCode.BOX.value:
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

def make_game_statistics_graph(df, statistics_type, league, matchup):
    '''
        Return figure

        Parameters
        ----------
        df - result of the get_play_by_play_data() function
        statistics_type - type of statistics to vizualize: score diff, points dynamic, etc.

        Returns
        -------
        Result figure
    '''

    home_team = find_team_info_by_abbreviation(league=league, abbreviation=matchup[:3])
    road_team = find_team_info_by_abbreviation(league=league, abbreviation=matchup[-3:])

    # sort values
    df = df.sort_values(by=['period', 'periodTime'], ascending=[True, True])

    # init figure
    if statistics_type == StatisticsTypeCode.SCORE_DIFF.value:
        fig = px.scatter(
            data_frame=df,
            x='periodTime', y='scoreDiff',
            # markers=True,
            color='scoreDiff'
        )
        # fig.update_traces(connectgaps=True)
    if statistics_type == StatisticsTypeCode.PTS.value:
        fig = px.scatter(
            data_frame=df,
            x='periodTime', y='points',
            # markers=True,
            color='teamTricode'
        )
    elif statistics_type == StatisticsTypeCode.FG2M.value:
        fig = px.scatter(
            data_frame=df,
            x='periodTime', y='fg2m',
            color='teamTricode',
        )
    elif statistics_type == StatisticsTypeCode.FG3M.value:
        fig = px.scatter(
            data_frame=df,
            x='periodTime', y='fg3m',
            color='teamTricode',
        )
    elif statistics_type == StatisticsTypeCode.REB.value:
        fig = px.scatter(
            data_frame=df,
            x='periodTime', y='rebounds',
            color='teamTricode',
        )
    elif statistics_type == StatisticsTypeCode.AST.value:
        fig = px.scatter(
            data_frame=df,
            x='periodTime', y='assists',
            color='teamTricode'
        )

    fig.update_layout(
        title=dict(
            text=f'{home_team['full_name']} vs. {road_team['full_name']}',
            x=0.4, y=0.95
        ),
        coloraxis_showscale=False,
        showlegend=False
    )
    fig.update_xaxes(tickformat='%M:%S')

    # add images
    # logo_paths = [
    #     'streamlit_app/static/league_team_logo/' + league + '/' + str(home_team_id) + '.svg',
    #     'streamlit_app/static/league_team_logo/' + league + '/' + str(road_team_id) + '.svg'
    # ]

    return fig

def make_league_rating_graph(df, league):
    '''
        Return figure

        Parameters
        ----------
        df - dataframe with rating info for each team in the league

        Returns
        -------
        Result figure
    '''

    min_range = floor(min(
        df.E_OFF_RATING.agg({'min', 'max'}).loc['min'],
        df.E_DEF_RATING.agg({'min', 'max'}).loc['min']
    ))

    max_range = ceil(max(
        df.E_OFF_RATING.agg({'min', 'max'}).loc['max'],
        df.E_DEF_RATING.agg({'min', 'max'}).loc['max']
    ))

    axes_range = [min_range, max_range]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.E_OFF_RATING,
            y=df.E_DEF_RATING,
            mode='text',
            customdata=np.stack(
                arrays=(df.E_NET_RATING, df.TEAM_NAME),
                axis=-1
            ),
            text=[
                find_team_info_by_id(team_id=id, league=league, value='abbreviation')
                for id in df.TEAM_ID
            ],
            textfont=dict(
                color='gray'
            ),
            hovertemplate=
                "<b>%{customdata[1]}</b><br>"
                "Net Rating: %{customdata[0]:.1f}<br>"
                "Offensive Rating: %{x:.1f}<br>"
                "Defensive Rating: %{y:.1f}<br>"
                "<extra></extra>"
        )
    )

    # add team images
    # for team_id in df.TEAM_ID.unique():
    #     fig.add_layout_image(
    #         source=Image.open(f'streamlit_app/static/league_team_logo/{league}/{team_id}.png'),
    #         sizex=1.5,
    #         sizey=1.5,
    #         name=find_team_info_by_id(team_id=team_id, league=league, value='abbreviation'),
    #         xref='x',
    #         yref='y',
    #         # x=games.loc[(games["GAME_NUM"] == game_num) & (games["TEAM"]==t), "CUME_OFF_RATING"].values[0],
    #         # y=games.loc[(games["GAME_NUM"] == game_num) & (games["TEAM"]==t), "CUME_DEF_RATING"].values[0],
    #         layer='above',
    #         opacity=1, xanchor='center', yanchor='middle'
    #     )

    base_color = '#F4F3EE'

    # Base Layouts
    fig.update_layout(
        plot_bgcolor=base_color,
        height=800,
        width=800,
        margin_t=0
    )
    fig.update_xaxes(
        gridcolor=base_color,
        range=axes_range,
        showgrid=False
    )
    fig.update_yaxes(
        gridcolor=base_color,
        autorange='reversed',
        range=axes_range,
        showgrid=False
    )

    # Get center location of chart
    line_location = (axes_range[0]+axes_range[1])/2

    # define annotation color
    annotation_color = '#0A0403'

    # x-axis line pointing right
    fig.add_annotation(
        x=min_range,
        y=line_location,
        xref='x', yref='y',
        text='',
        showarrow=True,
        axref='x', ayref='y',
        ax=max_range,
        ay=line_location,
        arrowhead=3,
        arrowwidth=1,
        arrowcolor=annotation_color
    )

    # x-axis line pointing left
    fig.add_annotation(
        x=max_range,
        y=line_location,
        xref='x', yref='y',
        text='',
        showarrow=True,
        axref='x', ayref='y',
        ax=min_range,
        ay=line_location,
        arrowhead=3,
        arrowwidth=1,
        arrowcolor=annotation_color
    )
    # x-axis label
    fig.add_annotation(
        x=max_range-2.15,
        y=line_location+0.35,
        align='center',
        text=f'Offensive Efficiency',
        font=dict(size=14),
        showarrow=False,
        font_color=annotation_color
    )
    
    # y-axis line pointing down
    fig.add_annotation(
        x=line_location,
        y=min_range,
        xref='x', yref='y',
        text='',
        showarrow=True,
        axref='x', ayref='y',
        ax=line_location,
        ay=max_range,
        arrowhead=3,
        arrowwidth=1,
        arrowcolor=annotation_color
    )
    # y-axis line pointing up
    fig.add_annotation(
        x=line_location,
        y=max_range,
        xref='x', yref='y',
        text='',
        showarrow=True,
        axref='x', ayref='y',
        ax=line_location,
        ay=min_range,
        arrowhead=3,
        arrowwidth=1,
        arrowcolor=annotation_color
    )
    fig.add_annotation(
        x=line_location,
        y=max_range+0.5,
        align='center',
        text=f'Defensive Efficiency',
        font=dict(size=14),
        showarrow=False,
        textangle=0,
        font_color=annotation_color
    )

    # diagonal line
    fig.add_shape(
        type="line",
        # starting coordinates
        x0=min_range+0.5, y0=min_range+0.5,
        # ending coordinates
        x1=max_range-0.5, y1=max_range-0.5,
        # Make sure the points are on top of the line
        layer="below",
        # Style it like the axis lines
        line=dict(dash='dash', color='gray', width=1)
    )

    # diagonal annotation -> positive/negative teams
    fig.add_annotation(
        x=min_range+3.5,
        y=min_range,
        align='left',
        text=f'Positive Teams',
        font=dict(size=11, color='gray'),
        showarrow=False,
        textangle=0,
    )
    fig.add_annotation(
        x=min_range+1.5,
        y=min_range+3.5,
        align='left',
        text=f'Negative Teams',
        font=dict(size=11, color='gray'),
        showarrow=False,
        textangle=0
    )

    return fig