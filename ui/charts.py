from __future__ import annotations

import pandas as pd
import altair as alt


def weekly_trend_chart(
    weekly_df: pd.DataFrame,
    col: str,
    title: str,
    chart_type: str,
    bar_size: int = 18,
    bar_color: str = "#4C78A8",
    line_color: str = "#F58518",
) -> alt.Chart:
    d = weekly_df.copy()
    d["rolling_4w"] = d[col].rolling(4, min_periods=1).mean()

    base = alt.Chart(d).encode(
        x=alt.X(
            "start_of_week:T",
            title="Start of week",
            axis=alt.Axis(format="%Y-%m-%d", labelOverlap=True),
        ),
        tooltip=[
            alt.Tooltip("start_of_week:T", title="Week"),
            alt.Tooltip(f"{col}:Q", title=title, format=".2f"),
            alt.Tooltip("rolling_4w:Q", title="4-week avg", format=".2f"),
        ],
    )

    if chart_type == "bar":
        bars = base.mark_bar(size=bar_size).encode(
            y=alt.Y(f"{col}:Q", title=None),
            color=alt.value(bar_color),
        )

        rolling = base.mark_line(point=True).encode(
            y="rolling_4w:Q",
            color=alt.value(line_color),
        )

        chart = bars + rolling

    else:
        line = base.mark_line(point=True).encode(
            y=alt.Y(f"{col}:Q", title=None),
            color=alt.value(line_color),
        )

        rolling = base.mark_line().encode(
            y="rolling_4w:Q",
            color=alt.value(bar_color),
        )

        chart = line + rolling

    return chart.properties(height=500).interactive()
