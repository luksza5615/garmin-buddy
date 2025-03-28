import streamlit as st
from app.services.db_service import execute_azure, get_activities

if st.button("Refresh data"):
    execute_azure()

st.title("Last activities")
# if st.button("Get activities"):
activities = get_activities()
st.dataframe(activities)
