from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta

from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from garmin_buddy.ai.llm_analysis_service import LLMService
from garmin_buddy.analysis.analysis_service import AnalysisService
from garmin_buddy.database.db_connector import Database
from garmin_buddy.database.db_service import ActivityRepository
from garmin_buddy.ingestion.activity_mapper import ActivityMapper
from garmin_buddy.ingestion.fit_filestore import FitFileStore
from garmin_buddy.ingestion.fit_parser import FitParser
from garmin_buddy.ingestion.garmin_client import GarminClient
from garmin_buddy.orchestration.sync_service import SyncService
from garmin_buddy.settings.config import Config, ConfigError
from garmin_buddy.settings.logging_config import setup_logging
from garmin_buddy.ui.charts import weekly_trend_chart
from garmin_buddy.ui.label_mapping import SPORT_LABELS, SUBSPORT_LABELS


@dataclass(frozen=True)
class Services:
    repo: ActivityRepository
    sync: SyncService
    analysis: AnalysisService
    llm: LLMService


# @st.cache_resource(show_spinner=False)
def init_services() -> Services:
    load_dotenv(override=True)
    setup_logging()

    cfg = Config.from_env()
    db = Database.create_db(cfg)
    garmin = GarminClient(cfg.garmin_email, cfg.garmin_password)
    filestore = FitFileStore(cfg)
    parser = FitParser()
    mapper = ActivityMapper()
    repo = ActivityRepository(db)
    sync = SyncService(cfg, db, garmin, filestore, parser, mapper, repo)
    analysis = AnalysisService(repo)
    llm = LLMService(cfg.llm_api_key)

    return Services(repo=repo, sync=sync, analysis=analysis, llm=llm)


# @st.cache_data(ttl=60, show_spinner=False)
def load_activities(repo: ActivityRepository, start: date, end: date) -> pd.DataFrame:
    df = repo.get_activities(start, end)
    if df.empty:
        return df

    return df.sort_values(by="activity_start_time", ascending=False)


# ----------APP---------
def main():
    st.set_page_config(page_title="Garmin Buddy", layout="wide")

    try:
        services = init_services()
    except ConfigError as e:
        st.error(str(e))
        st.info("Set missing env vars (or .env) and restart the app.")
        st.stop()

    # st.title("Garmin Buddy")

    # --- Sidebar controls
    with st.sidebar:
        st.header("📅 Activities date range")

        default_end = date.today()
        default_start = default_end - timedelta(days=30)
        start, end = st.date_input(
            label="",
            value=(default_start, default_end),
            max_value=default_end,
            label_visibility="collapsed",
            format="DD/MM/YYYY",
        )

        st.divider()

        st.header("🔄 Refresh activities    ")
        if st.button("Refresh", width="stretch"):
            with st.spinner("Syncing activities..."):
                sync_start = start
                services.sync.sync_activities(sync_start)
            st.cache_data.clear()
            st.toast("Actitivies refreshed", icon="✅")

    # Load activities (cached)
    df = load_activities(services.repo, start, end)

    metrics = services.analysis.calculate_kpis(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Activities 🏋️", f"{int(metrics.get('activities_count', 0)):,.0f}")
    col2.metric("Distance ➡️", f"{metrics.get('distance_km', 0):,.2f} km")
    # TODO col2.metric("Duration", f"{metrics.get('duration_h', 0):.1f} h")
    col3.metric("Ascent ↗️", f"{metrics.get('ascent_m', 0):,.0f} m")
    col4.metric("Avg HR ❤️", f"{metrics.get('avg_hr', 0):.0f} bpm")

    tabs = st.tabs(["Activities", "Weekly", "AI Analysis"])

    with tabs[0]:
        st.subheader("Activities")
        if df.empty:
            st.info("No activities to show.")
        else:
            cols = [
                "activity_start_time",
                "sport",
                "subsport",
                "distance_in_km",
                "elapsed_duration",
                "grade_adjusted_avg_pace_min_per_km",
                "avg_heart_rate",
                "total_ascent_in_m",
                "calories_burnt",
                "aerobic_training_effect_0_to_5",
                "anaerobic_training_effect_0_to_5",
                "running_efficiency_index",
            ]

            display_df = df[cols].copy()
            display_df["sport"] = display_df["sport"].map(SPORT_LABELS)
            display_df["subsport"] = display_df["subsport"].map(SUBSPORT_LABELS)

            st.dataframe(
                display_df,
                hide_index=True,
                width="stretch",
                column_config={
                    "activity_start_time": st.column_config.DatetimeColumn(
                        "Start time"
                    ),
                    "sport": st.column_config.TextColumn("Sport"),
                    "subsport": st.column_config.TextColumn("Type"),
                    "distance_in_km": st.column_config.NumberColumn(
                        "Distance (km)", format="%.2f"
                    ),
                    "elapsed_duration": st.column_config.TextColumn("Duration"),
                    "grade_adjusted_avg_pace_min_per_km": st.column_config.TextColumn(
                        "Avg pace (min/km)"
                    ),
                    "avg_heart_rate": st.column_config.NumberColumn(
                        "Avg HR", format="%.0f"
                    ),
                    "total_ascent_in_m": st.column_config.NumberColumn(
                        "Ascent (m)", format="%.0f"
                    ),
                    "calories_burnt": st.column_config.NumberColumn(
                        "Calories", format="%.0f"
                    ),
                    "aerobic_training_effect_0_to_5": st.column_config.NumberColumn(
                        "Aerobic TE (0-5)", format="%.1f"
                    ),
                    "anaerobic_training_effect_0_to_5": st.column_config.NumberColumn(
                        "Anaerobic TE (0-5)", format="%.1f"
                    ),
                    "running_efficiency_index": st.column_config.NumberColumn(
                        "Running Efficiency Index", format="%.2f"
                    ),
                },
            )

    with tabs[1]:
        st.subheader("Weekly measures for running")
        w = services.analysis.weekly_running_stats(df)

        if w.empty:
            st.info("No running activities in this range.")
        else:
            METRICS = {
                "Distance": {"col": "distance_km", "type": "bar"},
                "Calories": {"col": "calories", "type": "bar"},
                "Average HR": {"col": "avg_hr", "type": "line"},
                "Running efficiency index": {"col": "rei", "type": "line"},
                "Ascent": {"col": "ascent_m", "type": "bar"},
                "Average aerobic TE": {"col": "te_aer", "type": "line"},
                "Average anaerobic TE": {"col": "te_ana", "type": "line"},
            }

            metric_label = st.radio(
                "Metric",
                options=list(METRICS.keys()),
                horizontal=True,
                label_visibility="collapsed",
            )

            metric_cfg = METRICS[metric_label]
            col = metric_cfg["col"]

            chart = weekly_trend_chart(
                weekly_df=w,
                col=col,
                title=metric_label,
                chart_type=metric_cfg["type"],
                bar_size=18,
                bar_color="#4C78A8",
                line_color="#F58518",
            )
            st.altair_chart(chart)

            st.dataframe(
                w,
                width="stretch",
                hide_index=True,
                column_config={
                    "start_of_week": st.column_config.DateColumn("Start of week"),
                    "distance_km": st.column_config.NumberColumn(
                        "Distance (km)", format="%.2f"
                    ),
                    "avg_hr": st.column_config.NumberColumn("Avg HR", format="%.0f"),
                    "ascent_m": st.column_config.NumberColumn(
                        "Ascent (m)", format="%.0f"
                    ),
                    "calories": st.column_config.NumberColumn(
                        "Calories", format="%.0f"
                    ),
                    "te_aer": st.column_config.NumberColumn(
                        "Aerobic TE (0-5)", format="%.1f"
                    ),
                    "te_ana": st.column_config.NumberColumn(
                        "Anaerobic TE (0-5)", format="%.1f"
                    ),
                    "rei": st.column_config.NumberColumn(
                        "Running Efficiency Index", format="%.2f"
                    ),
                },
            )

    with tabs[2]:
        st.subheader("AI analysis")
        st.caption("Generates insights for the selected date range.")

        if df.empty:
            st.info("Pick a range with activities first.")
        else:
            if st.button("🤖 Generate AI analysis", type="primary"):
                with st.spinner("Analyzing..."):
                    analysis_text = services.llm.analyze_training_period(
                        df, metrics, start, end
                    )
                st.markdown(analysis_text)
