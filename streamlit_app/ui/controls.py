import streamlit as st
from streamlit_javascript import st_javascript

from datetime import datetime
from dateutil.relativedelta import relativedelta

from utils.league import LEAGUE, league_value_by_key
from utils.season import SEASON_YEAR, SEASON_TYPE, SeasonTypeCode, season_type_value_by_key
from utils.teams import get_league_teams, find_team_full_name_by_id

def selected_page():
    '''
        Returns url and page name of the selected page

        Returns
        -------
        dict:
            url - url path
            page - page name
    '''
    url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    page = url.rsplit('/', 1)[1]

    return {
        'url': url,
        'page': page
    }

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
    
    return find_team_full_name_by_id(league=league, team_id=team_id)

def main_controls():
    '''
        Returns ui container with widgets used across multiple pages
    '''

    with st.sidebar:
        st.selectbox(
            label='League', key='league',
            options=LEAGUE,
            format_func=league_value_by_key
        )

        st.selectbox(
            label='Season', key='season',
            options=SEASON_YEAR[st.session_state.league]
        )

        st.multiselect(
            label='Season Type', key='season_type',
            options=SEASON_TYPE,
            default=[SeasonTypeCode.PLAYOFF.value, SeasonTypeCode.REGULAR.value],
            format_func=season_type_value_by_key,
            help='Unselected season type means all season types.'
        )

        st.divider()

        st.selectbox(
            label='Base Team', key='team_base',
            options=define_team_options(),
            format_func=format_team_options
        )

        st.selectbox(
            label='Matchup Team', key='team_matchup',
            options=define_team_options(),
            format_func=format_team_options,
            index=None,
            # disabled=st.session_state.team_1 is None,
            help='The second team can only be selected after the first team has been selected.'
        )

        st.toggle(label='Include Date Range', key='toggle_date_range', value=False)
        
        if st.session_state.toggle_date_range:
            st.session_state.date_range = [
                datetime.today().date() - relativedelta(days=30),
                datetime.today().date()
            ]
            
            st.date_input(
                label='Date', key='date_range',
                max_value=datetime.today().date(),
                help='Use to filter by game dates. By default last 30 days interval is selected.'
            )
        else:
            st.session_state.date_range = None