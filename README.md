# 🎯 AI-Powered Digital Marketing Campaign Analyzer

> A full-stack GenAI pipeline that analyzes marketing campaign data, generates AI-driven insights, suggests optimizations, automates reporting, and generates ad copy — powered by Claude (Anthropic).

---

## 🚀 Live Demo

> Run locally in 60 seconds — see setup below.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=flat-square&logo=streamlit)
![Claude API](https://img.shields.io/badge/Claude-Sonnet-purple?style=flat-square)
![Plotly](https://img.shields.io/badge/Plotly-5.18-green?style=flat-square&logo=plotly)

---

## 📸 Features

| Module | Description |
|--------|-------------|
| 📊 **Dashboard** | Interactive charts — ROAS bars, spend vs revenue scatter, platform breakdown, CTR/CPC heatmap, conversion funnel |
| 🤖 **AI Analysis** | Claude LLM analyzes all campaigns, flags underperformers, detects anomalies, gives optimization recommendations |
| 🔍 **Competitor Intel** | AI-powered competitor benchmarking — CTR, CPC, ROAS industry averages + strategic gaps |
| ✍️ **Ad Copy Generator** | Generate platform-optimized headlines, descriptions & CTAs for any campaign in one click |
| 📄 **PDF Report** | Auto-generate a branded, professional PDF report with AI insights + full campaign data table |

---

## 🛠️ Tech Stack

- **Language**: Python 3.11
- **LLM**: Claude Sonnet via Anthropic API
- **Frontend**: Streamlit
- **Charts**: Plotly
- **PDF Generation**: FPDF2
- **Data Processing**: Pandas
- **Deployment**: Streamlit Cloud (free)

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-marketing-analyzer.git
cd ai-marketing-analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
# Get one free at: https://console.anthropic.com
```

### 4. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` 🎉

---

## 📁 Project Structure

```
ai-marketing-analyzer/
├── app.py                    # Main Streamlit dashboard
├── src/
│   ├── data_processor.py     # CSV ingestion, KPI computation, flagging
│   ├── llm_engine.py         # Claude API integration
│   ├── charts.py             # Plotly visualization functions
│   └── report_generator.py  # PDF report generation
├── data/
│   └── sample_campaigns.csv  # 15 sample campaigns (Google, Meta, LinkedIn)
├── prompts/
│   ├── analysis_system_prompt.txt   # LLM system prompt for campaign analysis
│   └── competitor_prompt.txt        # LLM prompt for competitor intelligence
├── reports/                  # Auto-generated PDF reports (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```

---

## 💡 How It Works

### Data Pipeline
1. Upload your campaign CSV (or use the included sample data)
2. `data_processor.py` computes KPIs and flags campaigns (Top Performer / Underperformer / Critical)
3. Formatted data is passed as structured JSON to the LLM

### AI Analysis Engine
1. Campaign JSON is sent to Claude with a detailed system prompt
2. Claude returns structured JSON: executive summary, top performers, underperformers, anomalies, recommendations
3. Results are displayed in a rich UI and can be exported to PDF

### Report Generation
- `report_generator.py` uses FPDF2 to produce a multi-page branded PDF
- Includes KPI cards, AI insights, recommendations, budget plan, and full data table

---

## 📊 Sample Output

**Campaigns tracked**: 15 (Google Ads, Meta Ads, LinkedIn, Microsoft Ads)  
**Platforms covered**: 4  
**KPIs computed**: ROAS, CTR, CPC, CPA, Conversions, Impressions, Revenue  
**AI modules**: Analysis, Competitor Intel, Ad Copy Generation

---

## 🔧 Customization

- **Add your own data**: Replace `data/sample_campaigns.csv` with your real campaign export
- **Modify prompts**: Edit files in `prompts/` to change what Claude analyzes
- **Add platforms**: Extend `data_processor.py` to support TikTok Ads, Snapchat, etc.
- **Extend charts**: Add new Plotly charts in `charts.py`

---

## 🚀 Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add `ANTHROPIC_API_KEY` in Streamlit secrets
5. Deploy — live URL in 2 minutes ✅

---

## 👨‍💻 Author

Built as a portfolio project aligned with AI/Digital Marketing roles.  
Demonstrates: GenAI integration, prompt engineering, marketing automation, data analysis, PDF generation.

---

## 📄 License

MIT License — free to use and modify.
