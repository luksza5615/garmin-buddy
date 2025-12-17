import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import logging 
from app.services.db_service import get_activities, get_top_activities, refresh_db, get_last_activity
from app.services.garmin_service import sync_all_activities
from app.services.llm_google_service import generate_response, build_prompt
from app.services.weekly_analysis_service import analyze_training_period, get_training_summary
from app.config import Config

st.set_page_config(page_title='Garmin Buddy', layout='wide')

configuration = Config.from_env()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="format=%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
setup_logging()

if st.button("Refresh database"):
    with st.spinner("Fetching last activities..."):
        sync_all_activities(configuration)
        # refresh_db()


activities_df = get_activities().sort_values(
    by="activity_start_time", ascending=False)


st.subheader("Activities")
st.dataframe(activities_df)

running_activities = activities_df[activities_df['sport'] == 'running']


st.subheader("Running weekly measures")
weekly_running_activities = running_activities.groupby("start_of_week").agg(
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

# Ensure missing weeks are shown as gaps (zero values)
# Convert to datetime for reliable weekly indexing
weekly_running_activities["start_of_week"] = pd.to_datetime(weekly_running_activities["start_of_week"]) 

if not weekly_running_activities.empty:
    # Build a complete weekly index from min to max, aligned to the same weekday as existing data
    first_week = weekly_running_activities["start_of_week"].min()
    last_week = weekly_running_activities["start_of_week"].max()
    # Assuming start_of_week is a Monday (consistent with calculation in garmin_service)
    full_weeks_index = pd.date_range(start=first_week, end=last_week, freq="W-MON")

    reindexed = weekly_running_activities.set_index("start_of_week").reindex(full_weeks_index)

    # Fill missing numeric columns with zeros to visualize gaps as empty bars
    numeric_cols = [
        "distance_in_km",
        "calories_burnt",
        "avg_heart_rate",
        "total_ascent_in_meters",
        "running_efficiency_index",
        "aerobic_training_effect_0_to_5",
        "anaerobic_training_effect_0_to_5",
    ]
    for col in numeric_cols:
        if col in reindexed.columns:
            reindexed[col] = reindexed[col].fillna(0)

    weekly_running_activities = reindexed.reset_index().rename(columns={"index": "start_of_week"})

st.dataframe(weekly_running_activities)

# Pagination setup
page_size = 20
total_pages = len(weekly_running_activities) // page_size + \
    (1 if len(weekly_running_activities) % page_size else 0)

# Use session state to persist current page and control via buttons below the chart
if "weekly_page" not in st.session_state:
    st.session_state["weekly_page"] = 1

page = max(1, min(st.session_state["weekly_page"], max(total_pages, 1)))

start_idx = (page - 1) * page_size
end_idx = start_idx + page_size
df_page = weekly_running_activities.sort_values(
    by="start_of_week", ascending=False
).iloc[start_idx:end_idx].reset_index(drop=True)
# Within the page, show oldest on the left and newest on the right
df_page = df_page.sort_values(by="start_of_week", ascending=True).reset_index(drop=True)

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
# Format x-axis as YYYY-MM-DD without time
if isinstance(df_page["start_of_week"].iloc[0], pd.Timestamp):
    x_labels = df_page["start_of_week"].dt.strftime('%Y-%m-%d').tolist()
else:
    # fallback if dtype is object/str
    x_labels = pd.to_datetime(df_page["start_of_week"]).dt.strftime('%Y-%m-%d').tolist()
ax.set_xticklabels(x_labels, fontsize=3, rotation=45, ha='right')


ax.tick_params(axis='both', labelsize=3)
ax2.tick_params(axis='y', labelsize=3)


# Hide labels for zero-height bars by using empty strings
distance_labels = [f"{v:.2f}" if float(v) > 0 else "" for v in df_page["distance_in_km"]]
calories_labels = [f"{int(v)}" if float(v) > 0 else "" for v in df_page["calories_burnt"]]
ax.bar_label(bars, labels=distance_labels, padding=2, fontsize=3)
ax2.bar_label(bars2, labels=calories_labels, padding=2, fontsize=3)

st.pyplot(fig)

# Pagination controls under the chart (compact and centered)
pad_left, prev_col, page_col, next_col, pad_right = st.columns([4, 1, 1, 1, 4])

with prev_col:
    if st.button("< Previous", disabled=page <= 1):
        st.session_state["weekly_page"] = max(1, page - 1)
        st.rerun()

with page_col:
    st.markdown(
        f"<div style='text-align:center; white-space:nowrap;'>Page {page} / {total_pages}</div>",
        unsafe_allow_html=True,
    )

with next_col:
    if st.button("Next >", disabled=page >= total_pages):
        st.session_state["weekly_page"] = min(total_pages, page + 1)
        st.rerun()

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


# Weekly Analysis Section
st.subheader("📊 Training Period Analysis")

# Create columns for day selection and analysis
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    days_option = st.selectbox(
        "Analysis Period",
        options=[7, 10, 14, 21, 30],
        index=0,
        help="Select number of days to analyze"
    )

with col2:
    if st.button("📈 Analyze Training Period", type="primary"):
        with st.spinner(f"Analyzing last {days_option} days..."):
            try:
                # Get quick summary first
                summary = get_training_summary(days_option)
                
                # Display summary metrics
                st.success(f"Found {summary['activities_count']} activities in the last {days_option} days")
                
                # Show metrics in columns
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.metric("Total Distance", f"{summary['metrics']['total_distance_km']:.1f} km")
                    st.metric("Total Activities", summary['metrics']['total_activities'])
                
                with metric_col2:
                    st.metric("Avg Heart Rate", f"{summary['metrics']['avg_heart_rate']:.0f} bpm")
                    st.metric("Total Calories", f"{summary['metrics']['total_calories']:,}")
                
                with metric_col3:
                    st.metric("Total Duration", f"{summary['metrics']['total_duration_hours']:.1f} hrs")
                    st.metric("Elevation Gain", f"{summary['metrics']['total_ascent_m']:,} m")
                
                # Sports breakdown
                if summary['metrics']['sports_breakdown']:
                    st.write("**Sports Breakdown:**")
                    for sport, count in summary['metrics']['sports_breakdown'].items():
                        st.write(f"- {sport}: {count} activities")
                
                # Get detailed analysis
                st.write("---")
                st.write("**🤖 AI Analysis:**")
                analysis = analyze_training_period(days_option)
                st.write(analysis)
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")

with col3:
    st.info(f"""
    **Analysis Period: {days_option} days**
    
    This analysis will examine your training data from the last {days_option} days, including:
    - Training load and volume
    - Performance trends
    - Recovery patterns
    - Sport-specific insights
    - Personalized recommendations
    """)

# Quick Summary Section
if st.button("📋 Quick Summary"):
    with st.spinner("Generating quick summary..."):
        try:
            summary = get_training_summary(days_option)
            
            st.subheader(f"Quick Summary - Last {days_option} Days")
            
            # Create a more detailed metrics display
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Training Volume:**")
                st.write(f"- Total Distance: {summary['metrics']['total_distance_km']:.1f} km")
                st.write(f"- Total Duration: {summary['metrics']['total_duration_hours']:.1f} hours")
                st.write(f"- Total Activities: {summary['metrics']['total_activities']}")
                
            with col2:
                st.write("**Performance Metrics:**")
                st.write(f"- Average Heart Rate: {summary['metrics']['avg_heart_rate']:.0f} bpm")
                st.write(f"- Total Calories: {summary['metrics']['total_calories']:,}")
                st.write(f"- Elevation Gain: {summary['metrics']['total_ascent_m']:,} m")
            
            # Date range
            st.write(f"**Period:** {summary['date_range']['start']} to {summary['date_range']['end']}")
            
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")


