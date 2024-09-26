import streamlit as st

from ui.controls import main_controls, selected_page

# define pages
league_page = st.Page(page='ui/pages/league.py', title='League')
team_page = st.Page(page='ui/pages/team.py', title='Team')
game_page = st.Page(page='ui/pages/game.py', title='Game')

# define navigation
pg = st.navigation(
    pages=[
        league_page,
        team_page,
        game_page
    ]
)

# set global confiugs
st.set_page_config(
    page_title='Basketball Insights',
    layout='wide',
    menu_items={
        'About': "App development in progres..."
    }
)

st.text(
    '''
        App development in progres...
    '''
)

# main controls that will be used across pages
main_controls()

# dev info
# st.write(selected_page())
# st.write(st.session_state)

# run app
pg.run()