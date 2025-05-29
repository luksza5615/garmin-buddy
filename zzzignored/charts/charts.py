import streamlit as st
import pandas as pd
import numpy as np
# from ui.charts.distance_by_period import plot_distance
from app.services.db_service import get_aggregated_data

st.title("Dashboard")

df = pd.DataFrame({
    "date": pd.date_range(start="2023-01-01", periods=200, freq="D"),
    "distance_km": (np.random.rand(200) * 10).round(2)
})
df["date"] = pd.to_datetime(df["date"])


agg_level = st.selectbox("Aggregate by", ["Week", "Month", "Quarter", "Year"])
metric_option = st.radio("Select metric to show", [
                         "Total distance", "Total calories"])
df = get_aggregated_data(agg_level)
# st.bar_chart(df.set_index("start_of_week")["suma"])
df["suma"] = df["suma"].astype(float)
st.bar_chart(data=df, x="start_of_week", y="suma")

# fig = plot_distance(df, agg_level)
# st.plotly_chart(fig, use_container_width=True)
