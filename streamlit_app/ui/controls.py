import streamlit as st
from streamlit_javascript import st_javascript

from datetime import datetime

from utils.league import LEAGUE, format_league_options
from utils.season import SEASON_YEAR
from utils.teams import get_league_teams, find_team_info_by_id, format_team_options

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

def format_game_date(date_str):
    '''
        Format date string to `01 Jan, 2024` format
    '''
    date_dt = datetime.strptime(date_str, '%Y-%m-%d')

    date_str_formatted = datetime.strftime(date_dt, '%d %b, %Y')

    return date_str_formatted

def main_controls():
    '''
        Returns ui container with widgets used across multiple pages
    '''

    with st.sidebar:
        st.radio(
            label='League', key='league',
            options=LEAGUE,
            horizontal=True,
            format_func=format_league_options
        )

        st.radio(
            label='Season', key='season_year',
            options=SEASON_YEAR[st.session_state.league],
            horizontal=True
        )

        # st.divider()

        # st.toggle(label='Include Date Range', key='toggle_date_range', value=False)
        
        # if st.session_state.toggle_date_range:
        #     st.session_state.date_range = [
        #         datetime.today().date() - relativedelta(days=30),
        #         datetime.today().date()
        #     ]
            
        #     st.date_input(
        #         label='Date', key='date_range',
        #         max_value=datetime.today().date(),
        #         help='Use to filter by game dates. By default last 30 days interval is selected.'
        #     )
        # else:
        #     st.session_state.date_range = None