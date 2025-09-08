import streamlit as st
import matplotlib.pyplot as plt
from app.services.db_service import get_activities, get_top_activities, refresh_db, get_last_activity
from app.services.llm_google_service import generate_response, build_prompt

st.set_page_config(page_title='Garmin Buddy', layout='wide')

if st.button("Call chat"):
    with st.spinner("Generating response"):
        workout = get_last_activity()
        prompt = build_prompt(workout)
        response = generate_response(prompt)
        st.write(response)
        st.text_area("Training summary", response)


if st.button("Refresh database"):
    with st.spinner("Fetching last activities..."):
        refresh_db()


activities_df = get_activities().sort_values(
    by="activity_start_time", ascending=False)

st.subheader("Data description")
st.write(activities_df.describe(include='all'))


st.subheader("Activities")
st.dataframe(activities_df)

sport_filter = st.selectbox("Filter by sport", activities_df['sport'].unique())
filtered_activities = activities_df[activities_df['sport'] == sport_filter]


st.subheader("Weekly measures")
weekly_activities = filtered_activities.groupby("start_of_week").agg(
    {
        "distance_in_km": "sum",
        "calories_burnt": "sum",
        "avg_heart_rate": "mean",
        "total_ascent_in_meters": "sum",
        "running_efficiency_index": "mean",
        "aerobic_training_effect_0_to_5": "mean",
        "anaerobic_training_effect_0_to_5": "mean"

    }
).reset_index().sort_values(
    by="start_of_week", ascending=False)
st.dataframe(weekly_activities)

page_size = 20
total_pages = len(weekly_activities) // page_size + \
    (1 if len(weekly_activities) % page_size else 0)
page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)

start_idx = (page - 1) * page_size
end_idx = start_idx + page_size
df_page = weekly_activities.iloc[start_idx:end_idx]
df_page = df_page.sort_values(
    "start_of_week", ascending=True).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(df_page))  # Numeric x positions for both axes
bar_width = 0.4

bars = ax.bar([i - bar_width/2 for i in x], df_page["distance_in_km"],
              width=bar_width, label="Distance (km)", color='tab:blue')

ax2 = ax.twinx()

bars2 = ax2.bar([i + bar_width/2 for i in x], df_page["calories_burnt"],
                width=bar_width, label="Calories Burnt", color='tab:orange')


ax.set_xlabel("Start of week", fontsize=5)
ax.set_ylabel("Distance (km)", fontsize=5, color='tab:blue')
ax2.set_ylabel("Calories Burnt", fontsize=5, color='tab:orange')


ax.set_xticks(x)
ax.set_xticklabels(df_page["start_of_week"],
                   fontsize=3, rotation=45, ha='right')


ax.tick_params(axis='both', labelsize=3)
ax2.tick_params(axis='y', labelsize=3)


ax.bar_label(bars, padding=2, fontsize=3)
ax2.bar_label(bars2, padding=2, fontsize=3)

st.pyplot(fig)

# RUNNING EFFICIENCY INDEX
fig2, ax = plt.subplots(figsize=(8, 4))
plt.plot(df_page["start_of_week"],
         df_page["running_efficiency_index"], marker='o')

ax.tick_params(axis='both', labelsize=3)
ax.set_xticks(df_page['start_of_week'])
ax.set_xticklabels(df_page["start_of_week"], rotation=45, fontsize=5)

ax.set_xlabel("Start of week", fontsize=5)
ax.set_ylabel("Average running efficiency index", fontsize=3)
st.pyplot(fig2)


if st.button("Summarize last trainings"):
    with st.spinner("Fetching an analyzing data..."):
        df = get_top_activities()
        # st.dataframe(df)
        # summary = test_ai()
        st.write(summary)
