import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


COLORS = {
    "primary": "#6C63FF",
    "success": "#00C896",
    "danger": "#FF4B6E",
    "warning": "#FFB340",
    "info": "#38BDF8",
    "muted": "#94A3B8",
    "bg": "#0F172A",
    "surface": "#1E293B",
    "text": "#F1F5F9",
}

CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color=COLORS["text"], size=13),
    margin=dict(l=10, r=10, t=40, b=10),
    colorway=[COLORS["primary"], COLORS["success"], COLORS["warning"],
              COLORS["info"], COLORS["danger"], "#A78BFA", "#34D399"],
)


def roas_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of ROAS by campaign with color-coded performance."""
    df_sorted = df.sort_values("roas", ascending=True)
    colors = [
        COLORS["danger"] if r < 1.5 else
        COLORS["warning"] if r < 3.0 else
        COLORS["success"]
        for r in df_sorted["roas"]
    ]
    fig = go.Figure(go.Bar(
        x=df_sorted["roas"],
        y=df_sorted["campaign_name"],
        orientation="h",
        marker_color=colors,
        text=[f"{r:.2f}x" for r in df_sorted["roas"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>ROAS: %{x:.2f}x<extra></extra>",
    ))
    fig.add_vline(x=1.0, line_dash="dash", line_color=COLORS["danger"],
                  annotation_text="Break-even", annotation_font_color=COLORS["danger"])
    fig.add_vline(x=3.0, line_dash="dash", line_color=COLORS["success"],
                  annotation_text="Good", annotation_font_color=COLORS["success"])
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="ROAS by Campaign", font=dict(size=16, color=COLORS["text"])),
        xaxis_title="ROAS (Return on Ad Spend)",
        height=max(350, len(df) * 35),
        showlegend=False,
    )
    return fig


def spend_vs_revenue_scatter(df: pd.DataFrame) -> go.Figure:
    """Bubble chart: Spend vs Revenue, bubble size = conversions."""
    flag_colors = {
        "Top Performer": COLORS["success"],
        "High Efficiency": COLORS["info"],
        "Normal": COLORS["primary"],
        "Underperformer": COLORS["warning"],
        "Critical - Losing Money": COLORS["danger"],
    }
    fig = go.Figure()
    for flag, group in df.groupby("flag"):
        fig.add_trace(go.Scatter(
            x=group["spend"],
            y=group["revenue"],
            mode="markers+text",
            name=flag,
            text=group["campaign_name"].str.split(" - ").str[0],
            textposition="top center",
            textfont=dict(size=10),
            marker=dict(
                size=group["conversions"] / group["conversions"].max() * 40 + 10,
                color=flag_colors.get(flag, COLORS["muted"]),
                opacity=0.85,
                line=dict(width=1, color="white"),
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Spend: $%{x:,.0f}<br>"
                "Revenue: $%{y:,.0f}<br>"
                "<extra></extra>"
            ),
        ))
    max_val = max(df["spend"].max(), df["revenue"].max()) * 1.1
    fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                  line=dict(dash="dot", color=COLORS["muted"], width=1))
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="Spend vs Revenue (bubble = conversions)", font=dict(size=16)),
        xaxis_title="Total Spend ($)",
        yaxis_title="Total Revenue ($)",
        height=480,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25),
    )
    return fig


def platform_breakdown_chart(platform_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart for platform comparison."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Spend vs Revenue by Platform", "Avg ROAS by Platform"),
        horizontal_spacing=0.12,
    )
    fig.add_trace(go.Bar(
        name="Spend", x=platform_df["platform"], y=platform_df["total_spend"],
        marker_color=COLORS["warning"], text=[f"${v:,.0f}" for v in platform_df["total_spend"]],
        textposition="outside",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        name="Revenue", x=platform_df["platform"], y=platform_df["total_revenue"],
        marker_color=COLORS["success"], text=[f"${v:,.0f}" for v in platform_df["total_revenue"]],
        textposition="outside",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        name="ROAS", x=platform_df["platform"], y=platform_df["avg_roas"],
        marker_color=COLORS["primary"], text=[f"{v:.2f}x" for v in platform_df["avg_roas"]],
        textposition="outside", showlegend=False,
    ), row=1, col=2)
    fig.update_layout(
        **CHART_THEME,
        height=400,
        barmode="group",
        title=dict(text="Platform Performance Breakdown", font=dict(size=16)),
    )
    return fig


def ctr_cpc_heatmap(df: pd.DataFrame) -> go.Figure:
    """Scatter: CTR vs CPC colored by ROAS — efficiency quadrant."""
    fig = go.Figure(go.Scatter(
        x=df["cpc"],
        y=df["ctr"],
        mode="markers+text",
        text=df["campaign_name"].str.split(" - ").str[0],
        textposition="top center",
        textfont=dict(size=9),
        marker=dict(
            size=14,
            color=df["roas"],
            colorscale=[[0, COLORS["danger"]], [0.4, COLORS["warning"]], [1, COLORS["success"]]],
            showscale=True,
            colorbar=dict(title="ROAS", thickness=12),
            line=dict(width=1, color="white"),
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "CPC: $%{x:.2f}<br>"
            "CTR: %{y:.1f}%<br>"
            "<extra></extra>"
        ),
    ))
    avg_ctr = df["ctr"].mean()
    avg_cpc = df["cpc"].mean()
    fig.add_hline(y=avg_ctr, line_dash="dash", line_color=COLORS["muted"],
                  annotation_text=f"Avg CTR: {avg_ctr:.1f}%")
    fig.add_vline(x=avg_cpc, line_dash="dash", line_color=COLORS["muted"],
                  annotation_text=f"Avg CPC: ${avg_cpc:.2f}")
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="CTR vs CPC Efficiency Map (color = ROAS)", font=dict(size=16)),
        xaxis_title="Cost Per Click ($)",
        yaxis_title="Click-Through Rate (%)",
        height=420,
    )
    return fig


def conversions_funnel(df: pd.DataFrame) -> go.Figure:
    """Funnel chart from impressions → clicks → conversions."""
    totals = {
        "Impressions": int(df["impressions"].sum()),
        "Clicks": int(df["clicks"].sum()),
        "Conversions": int(df["conversions"].sum()),
    }
    fig = go.Figure(go.Funnel(
        y=list(totals.keys()),
        x=list(totals.values()),
        textinfo="value+percent initial",
        marker=dict(color=[COLORS["info"], COLORS["primary"], COLORS["success"]]),
        connector=dict(line=dict(color=COLORS["muted"], width=1)),
    ))
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="Full Conversion Funnel", font=dict(size=16)),
        height=360,
    )
    return fig
