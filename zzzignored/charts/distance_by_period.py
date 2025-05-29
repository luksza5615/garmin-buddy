import pandas as pd
import plotly.express as px


def plot_distance(df: pd.DataFrame, agg_level: str):
    df = df.copy()

    if agg_level == "Week":
        df["period"] = df["date"].dt.to_period(
            "W").apply(lambda r: r.start_time)
    elif agg_level == "Month":
        df["period"] = df["date"].dt.to_period("M").dt.to_timestamp()
    elif agg_level == "Quarter":
        df["period"] = df["date"].dt.to_period("Q").dt.to_timestamp()
    elif agg_level == "Year":
        df["period"] = df["date"].dt.to_period("Y").dt.to_timestamp()
    else:
        raise ValueError(f"Unknown aggregation level: {agg_level}")

    if "period" not in df.columns:
        raise ValueError(
            "Missing 'period' column after aggregation assignment")

    agg_df = df.groupby("period", as_index=False)["distance_km"].sum()

    import plotly.express as px
    fig = px.bar(
        agg_df,
        x="period",
        y="distance_km",
        labels={"period": agg_level, "distance_km": "Total Distance (km)"},
        title=f"Total Distance per {agg_level}",
    )
    fig.update_layout(xaxis_title=agg_level,
                      yaxis_title="Distance (km)", hovermode="x unified")
    return fig
