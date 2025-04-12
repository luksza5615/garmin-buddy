import streamlit as st
from app.services.db_service import get_activities

# if st.button("Refresh data"):
#     execute_azure()

st.set_page_config(page_title='Training Dashboard', layout='wide')
st.title("Welcome in garmin buddy app")

st.markdown("Use the sidebar to navigate to different pages")

st.title("Last activities")
# if st.button("Get activities"):
activities = get_activities()
st.dataframe(activities)
