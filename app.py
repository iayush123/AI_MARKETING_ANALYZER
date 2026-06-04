import streamlit as st
import pandas as pd
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_processor import (
    load_campaign_data, compute_summary_metrics,
    flag_campaigns, prepare_for_llm,
    get_platform_breakdown, get_objective_breakdown,
)
from charts import (
    roas_bar_chart, spend_vs_revenue_scatter,
    platform_breakdown_chart, ctr_cpc_heatmap, conversions_funnel,
)
from llm_engine import analyze_campaigns, analyze_competitors, generate_ad_copy
from report_generator import generate_report

# ──────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────
st.set_page_config(
    page_title="AI Marketing Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .main { background-color: #0F172A; }
  .block-container { padding: 2rem 2rem 4rem; max-width: 1400px; }

  .hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.8rem; font-weight: 700;
    background: linear-gradient(135deg, #6C63FF 0%, #00C896 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.1;
  }
  .hero-sub { color: #94A3B8; font-size: 1rem; margin-top: 0.4rem; }

  .metric-card {
    background: #1E293B; border: 1px solid #334155;
    border-radius: 12px; padding: 1.2rem 1.4rem;
    border-left: 3px solid #6C63FF;
  }
  .metric-label { color: #64748B; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; }
  .metric-value { color: #F1F5F9; font-size: 1.8rem; font-weight: 600; font-family: 'Space Grotesk', sans-serif; margin-top: 0.2rem; }

  .insight-card {
    background: #1E293B; border: 1px solid #334155;
    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
  }
  .insight-title { color: #F1F5F9; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; }
  .insight-body { color: #94A3B8; font-size: 0.88rem; line-height: 1.6; }

  .badge-success { background: rgba(0,200,150,0.15); color: #00C896; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 500; }
  .badge-danger  { background: rgba(255,75,110,0.15);  color: #FF4B6E; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 500; }
  .badge-warning { background: rgba(255,179,64,0.15);  color: #FFB340; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 500; }
  .badge-info    { background: rgba(56,189,248,0.15);  color: #38BDF8; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 500; }

  .section-header {
    color: #F1F5F9; font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem; font-weight: 600; margin: 1.5rem 0 1rem;
    padding-bottom: 0.4rem; border-bottom: 1px solid #1E293B;
  }
  div[data-testid="stSidebar"] { background-color: #0F172A; border-right: 1px solid #1E293B; }
  div[data-testid="stSidebar"] .stMarkdown { color: #94A3B8; }

  .stDataFrame { border-radius: 10px; overflow: hidden; }
  .stButton > button {
    background: linear-gradient(135deg, #6C63FF, #A78BFA);
    color: white; border: none; border-radius: 8px;
    font-weight: 500; padding: 0.5rem 1.2rem;
    transition: all 0.2s;
  }
  .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(108,99,255,0.4); }

  .stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; }
  .stTabs [data-baseweb="tab"] {
    background: #1E293B; border-radius: 8px;
    color: #94A3B8; padding: 0.5rem 1.2rem; border: none;
  }
  .stTabs [aria-selected="true"] { background: #6C63FF !important; color: white !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 AI Marketing Analyzer")
    st.markdown("---")

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key from console.anthropic.com",
    )

    st.markdown("---")
    st.markdown("**Upload Campaign Data**")
    uploaded = st.file_uploader("CSV file", type=["csv"])

    st.markdown("---")
    st.markdown("**Industry (for competitor analysis)**")
    industry = st.text_input("e.g. E-commerce Fashion", value="E-commerce / D2C Brand")

    st.markdown("---")
    st.markdown("""
    <div style='color:#64748B; font-size:0.8rem;'>
    <b style='color:#94A3B8'>Metrics tracked</b><br>
    ROAS · CTR · CPC · CPA<br>Conversions · Impressions<br><br>
    <b style='color:#94A3B8'>Platforms</b><br>
    Google Ads · Meta Ads<br>LinkedIn · Microsoft Ads
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────
df_raw = load_campaign_data(uploaded_file=uploaded)
df = flag_campaigns(df_raw)
summary = compute_summary_metrics(df)
platform_df = get_platform_breakdown(df)
objective_df = get_objective_breakdown(df)

# ──────────────────────────────────────────
# HERO
# ──────────────────────────────────────────
col_hero, col_date = st.columns([4, 1])
with col_hero:
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
      <div class='hero-title'>AI Campaign Analyzer</div>
      <div class='hero-sub'>GenAI-powered performance intelligence for digital marketing teams</div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    ("Total Spend", f"${summary['total_spend']:,.0f}", "#FF4B6E"),
    ("Total Revenue", f"${summary['total_revenue']:,.0f}", "#00C896"),
    ("Portfolio ROAS", f"{summary['portfolio_roas']:.2f}x", "#6C63FF"),
    ("Conversions", f"{summary['total_conversions']:,}", "#38BDF8"),
    ("Avg CTR", f"{summary['avg_ctr']:.2f}%", "#FFB340"),
    ("Active Campaigns", str(summary["active_campaigns"]), "#A78BFA"),
]
for col, (label, val, color) in zip([c1, c2, c3, c4, c5, c6], kpis):
    with col:
        st.markdown(f"""
        <div class='metric-card' style='border-left-color:{color};'>
          <div class='metric-label'>{label}</div>
          <div class='metric-value' style='color:{color};'>{val}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────
# TABS
# ──────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "🤖 AI Analysis",
    "🔍 Competitor Intel",
    "✍️ Ad Copy Generator",
    "📄 Report",
])


# ═══════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>Campaign Performance Overview</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.plotly_chart(roas_bar_chart(df), use_container_width=True)
    with c2:
        st.plotly_chart(conversions_funnel(df), use_container_width=True)

    st.markdown("<div class='section-header'>Efficiency Analysis</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(spend_vs_revenue_scatter(df), use_container_width=True)
    with c2:
        st.plotly_chart(ctr_cpc_heatmap(df), use_container_width=True)

    st.markdown("<div class='section-header'>Platform Breakdown</div>", unsafe_allow_html=True)
    st.plotly_chart(platform_breakdown_chart(platform_df), use_container_width=True)

    st.markdown("<div class='section-header'>All Campaign Data</div>", unsafe_allow_html=True)
    flag_colors = {
        "Top Performer": "background-color: rgba(0,200,150,0.1)",
        "High Efficiency": "background-color: rgba(56,189,248,0.1)",
        "Underperformer": "background-color: rgba(255,179,64,0.1)",
        "Critical - Losing Money": "background-color: rgba(255,75,110,0.15)",
    }
    display_cols = ["campaign_name", "platform", "objective", "spend", "revenue",
                    "roas", "ctr", "cpc", "cpa", "conversions", "status", "flag"]
    st.dataframe(df[display_cols], use_container_width=True, height=420)


# ═══════════════════════════════════════════
# TAB 2 — AI ANALYSIS
# ═══════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>AI-Powered Campaign Analysis</div>", unsafe_allow_html=True)

    if not api_key:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar to enable AI analysis.")
    else:
        if st.button("🚀 Run Full AI Analysis", key="run_analysis"):
            with st.spinner("Claude is analyzing your campaigns..."):
                try:
                    campaign_json = prepare_for_llm(df)
                    result = analyze_campaigns(campaign_json, api_key)
                    st.session_state["analysis"] = result
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    if "analysis" in st.session_state:
        result = st.session_state["analysis"]

        st.markdown("#### 📋 Executive Summary")
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-body'>{result.get('executive_summary', '')}</div>
        </div>""", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### 🏆 Top Performers")
            performers = result.get("top_performers", [])
            for p in performers:
                if isinstance(p, dict):
                    name = p.get("campaign_name", p.get("name", ""))
                    reason = p.get("reason", p.get("why", ""))
                    st.markdown(f"""<div class='insight-card'>
                        <div class='insight-title'>✦ {name} <span class='badge-success'>Top</span></div>
                        <div class='insight-body'>{reason}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class='insight-card'>
                        <div class='insight-body'>✦ {p}</div>
                    </div>""", unsafe_allow_html=True)

        with col_b:
            st.markdown("#### ⚠️ Underperformers")
            underperformers = result.get("underperformers", [])
            for u in underperformers:
                if isinstance(u, dict):
                    name = u.get("campaign_name", u.get("name", ""))
                    problem = u.get("problem", u.get("issue", ""))
                    st.markdown(f"""<div class='insight-card'>
                        <div class='insight-title'>⚠ {name} <span class='badge-danger'>Critical</span></div>
                        <div class='insight-body'>{problem}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class='insight-card'>
                        <div class='insight-body'>⚠ {u}</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("#### 💡 Optimization Recommendations")
        recs = result.get("recommendations", [])
        for rec in recs:
            if isinstance(rec, dict):
                camp = rec.get("campaign", rec.get("campaign_name", ""))
                action = rec.get("action", rec.get("recommendation", str(rec)))
                st.markdown(f"""<div class='insight-card'>
                    <div class='insight-title'>🎯 {camp}</div>
                    <div class='insight-body'>{action}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class='insight-card'>
                    <div class='insight-body'>→ {rec}</div>
                </div>""", unsafe_allow_html=True)

        anomalies = result.get("anomalies", "")
        if anomalies:
            st.markdown("#### 🔍 Anomalies Detected")
            st.markdown(f"""<div class='insight-card'>
                <div class='insight-body'>{anomalies if isinstance(anomalies, str) else json.dumps(anomalies, indent=2)}</div>
            </div>""", unsafe_allow_html=True)

        projection = result.get("projected_improvement", "")
        if projection:
            st.markdown("#### 📈 Projected Improvement")
            st.markdown(f"""<div class='insight-card'>
                <div class='insight-body' style='color:#00C896;'>{projection}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 3 — COMPETITOR INTEL
# ═══════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>Competitor Intelligence & Benchmarking</div>", unsafe_allow_html=True)

    if not api_key:
        st.warning("⚠️ Please enter your Anthropic API key to enable competitor analysis.")
    else:
        if st.button("🔍 Run Competitor Analysis", key="run_competitor"):
            with st.spinner("Analyzing competitor landscape..."):
                try:
                    camp_summary = f"Portfolio ROAS: {summary['portfolio_roas']}, Avg CTR: {summary['avg_ctr']}%, Avg CPC: ${summary['avg_cpc']}"
                    comp_result = analyze_competitors(industry, camp_summary, api_key)
                    st.session_state["competitor"] = comp_result
                    st.success("✅ Competitor analysis complete!")
                except Exception as e:
                    st.error(f"Competitor analysis failed: {e}")

    if "competitor" in st.session_state:
        comp = st.session_state["competitor"]

        st.markdown("#### 🌐 Competitor Landscape")
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-body'>{comp.get('competitor_landscape', '')}</div>
        </div>""", unsafe_allow_html=True)

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.markdown("**📊 CTR Benchmarks**")
            benchmarks = comp.get("benchmark_ctrs", {})
            if isinstance(benchmarks, dict):
                for k, v in benchmarks.items():
                    st.markdown(f"`{k}`: {v}")
            else:
                st.write(benchmarks)

        with col_b2:
            st.markdown("**💰 CPC Benchmarks**")
            cpc_bench = comp.get("benchmark_cpc", {})
            if isinstance(cpc_bench, dict):
                for k, v in cpc_bench.items():
                    st.markdown(f"`{k}`: {v}")
            else:
                st.write(cpc_bench)

        with col_b3:
            st.markdown("**📈 ROAS Benchmarks**")
            roas_bench = comp.get("benchmark_roas", {})
            if isinstance(roas_bench, dict):
                for k, v in roas_bench.items():
                    st.markdown(f"`{k}`: {v}")
            else:
                st.write(roas_bench)

        st.markdown("#### 🎯 Strategic Recommendations")
        strat = comp.get("strategic_recommendations", [])
        if isinstance(strat, list):
            for s in strat:
                st.markdown(f"""<div class='insight-card'>
                    <div class='insight-body'>→ {s}</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 4 — AD COPY GENERATOR
# ═══════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-header'>AI Ad Copy Generator</div>", unsafe_allow_html=True)

    if not api_key:
        st.warning("⚠️ Please enter your Anthropic API key to generate ad copy.")
    else:
        campaign_names = df["campaign_name"].tolist()
        selected_camp = st.selectbox("Select Campaign", campaign_names)
        camp_row = df[df["campaign_name"] == selected_camp].iloc[0]

        col_x, col_y = st.columns(2)
        with col_x:
            st.info(f"**Platform:** {camp_row['platform']} | **Objective:** {camp_row['objective']}")
        with col_y:
            st.info(f"**ROAS:** {camp_row['roas']:.2f}x | **CTR:** {camp_row['ctr']:.1f}% | **Status:** {camp_row['status']}")

        if st.button("✨ Generate Ad Copy", key="gen_copy"):
            with st.spinner("Claude is crafting your ad copy..."):
                try:
                    copy_result = generate_ad_copy(
                        selected_camp,
                        camp_row["objective"],
                        camp_row["platform"],
                        api_key,
                    )
                    st.session_state["ad_copy"] = copy_result
                except Exception as e:
                    st.error(f"Ad copy generation failed: {e}")

    if "ad_copy" in st.session_state:
        copy = st.session_state["ad_copy"]
        st.markdown("#### Generated Ad Copy")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""<div class='insight-card'>
                <div class='insight-title'>Headlines</div>""", unsafe_allow_html=True)
            for i in range(1, 4):
                h = copy.get(f"headline_{i}", "")
                if h:
                    st.markdown(f"**H{i}:** {h}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"""<div class='insight-card'>
                <div class='insight-title'>Call to Action</div>
                <div class='insight-body' style='font-size:1.1rem; color:#6C63FF; font-weight:600;'>
                {copy.get('cta_text', '')}
                </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class='insight-card'>
                <div class='insight-title'>Descriptions</div>""", unsafe_allow_html=True)
            for i in range(1, 3):
                d = copy.get(f"description_{i}", "")
                if d:
                    st.markdown(f"**D{i}:** {d}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"""<div class='insight-card'>
                <div class='insight-title'>Audience Targeting Suggestion</div>
                <div class='insight-body'>{copy.get('targeting_suggestion', '')}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown(f"**Tone:** `{copy.get('tone', '')}`")


# ═══════════════════════════════════════════
# TAB 5 — REPORT
# ═══════════════════════════════════════════
with tab5:
    st.markdown("<div class='section-header'>Generate PDF Report</div>", unsafe_allow_html=True)

    analysis_ready = "analysis" in st.session_state

    if not analysis_ready:
        st.info("ℹ️ Run the AI Analysis first (Tab 2) to include AI insights in the report. You can still generate a data-only report.")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("""<div class='insight-card'>
            <div class='insight-title'>📄 What's included</div>
            <div class='insight-body'>
            ✦ Portfolio KPI summary cards<br>
            ✦ AI executive summary<br>
            ✦ Top performers & underperformers<br>
            ✦ Optimization recommendations<br>
            ✦ Budget reallocation plan<br>
            ✦ Projected improvement<br>
            ✦ Full campaign data table
            </div>
        </div>""", unsafe_allow_html=True)

    with col_r2:
        st.markdown("""<div class='insight-card'>
            <div class='insight-title'>📊 Report stats</div>
            <div class='insight-body'>
            ✦ Auto-generated in seconds<br>
            ✦ Professional PDF format<br>
            ✦ Branded with Digidarts-ready layout<br>
            ✦ Includes all 15 campaign rows<br>
            ✦ Download & share instantly
            </div>
        </div>""", unsafe_allow_html=True)

    if st.button("📥 Generate & Download Report"):
        with st.spinner("Generating PDF report..."):
            try:
                analysis_data = st.session_state.get("analysis", {
                    "executive_summary": "Report generated without AI analysis. Run AI Analysis tab for full insights.",
                    "top_performers": [],
                    "underperformers": [],
                    "recommendations": [],
                })
                pdf_bytes = generate_report(df, summary, analysis_data)
                from datetime import datetime
                fname = f"campaign_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_bytes,
                    file_name=fname,
                    mime="application/pdf",
                )
                st.success("✅ Report ready! Click above to download.")
            except Exception as e:
                st.error(f"Report generation failed: {e}")
