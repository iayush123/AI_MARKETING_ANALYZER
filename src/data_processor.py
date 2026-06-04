import pandas as pd
import json
from pathlib import Path


def load_campaign_data(file_path=None, uploaded_file=None) -> pd.DataFrame:
    """Load campaign data from CSV file or uploaded Streamlit file."""
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif file_path:
        df = pd.read_csv(file_path)
    else:
        default_path = Path(__file__).parent.parent / "data" / "sample_campaigns.csv"
        df = pd.read_csv(default_path)
    return df


def compute_summary_metrics(df: pd.DataFrame) -> dict:
    """Compute portfolio-level KPI summary."""
    active = df[df["status"] == "Active"]
    return {
        "total_campaigns": len(df),
        "active_campaigns": len(active),
        "total_spend": round(df["spend"].sum(), 2),
        "total_revenue": round(df["revenue"].sum(), 2),
        "total_conversions": int(df["conversions"].sum()),
        "total_impressions": int(df["impressions"].sum()),
        "total_clicks": int(df["clicks"].sum()),
        "avg_roas": round(df["roas"].mean(), 2),
        "avg_ctr": round(df["ctr"].mean(), 2),
        "avg_cpc": round(df["cpc"].mean(), 2),
        "avg_cpa": round(df["cpa"].mean(), 2),
        "portfolio_roas": round(df["revenue"].sum() / df["spend"].sum(), 2),
        "best_campaign": df.loc[df["roas"].idxmax(), "campaign_name"],
        "worst_campaign": df.loc[df["roas"].idxmin(), "campaign_name"],
    }


def flag_campaigns(df: pd.DataFrame) -> pd.DataFrame:
    """Add status flags to each campaign for quick identification."""
    df = df.copy()
    df["flag"] = "Normal"
    df.loc[df["roas"] >= 4.0, "flag"] = "Top Performer"
    df.loc[(df["roas"] < 1.5) & (df["spend"] > 5000), "flag"] = "Underperformer"
    df.loc[df["roas"] < 1.0, "flag"] = "Critical - Losing Money"
    df.loc[(df["ctr"] > 6.0) & (df["roas"] >= 3.0), "flag"] = "High Efficiency"
    return df


def prepare_for_llm(df: pd.DataFrame) -> str:
    """Convert dataframe to clean JSON string for LLM consumption."""
    records = df.to_dict(orient="records")
    clean = []
    for r in records:
        clean.append({
            "campaign_name": r["campaign_name"],
            "platform": r["platform"],
            "objective": r["objective"],
            "spend": r["spend"],
            "revenue": r["revenue"],
            "roas": r["roas"],
            "ctr": r["ctr"],
            "cpc": r["cpc"],
            "cpa": r["cpa"],
            "conversions": r["conversions"],
            "impressions": r["impressions"],
            "clicks": r["clicks"],
            "quality_score": r.get("quality_score", "N/A"),
            "status": r["status"],
        })
    return json.dumps(clean, indent=2)


def get_platform_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate metrics by platform."""
    return df.groupby("platform").agg(
        total_spend=("spend", "sum"),
        total_revenue=("revenue", "sum"),
        avg_roas=("roas", "mean"),
        avg_ctr=("ctr", "mean"),
        total_conversions=("conversions", "sum"),
        campaign_count=("campaign_id", "count"),
    ).round(2).reset_index()


def get_objective_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate metrics by campaign objective."""
    return df.groupby("objective").agg(
        total_spend=("spend", "sum"),
        total_revenue=("revenue", "sum"),
        avg_roas=("roas", "mean"),
        avg_cpa=("cpa", "mean"),
        campaign_count=("campaign_id", "count"),
    ).round(2).reset_index()
