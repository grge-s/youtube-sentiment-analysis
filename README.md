# YouTube Sentiment Analysis — ChatGPT Public Perception

**Analyst:** George Shaheen
**Date:** September 2024

---

## 📋 Project Overview

This project uses Natural Language Processing (NLP) to analyse public sentiment toward ChatGPT across YouTube comment data. The analysis spans **15 query categories** (covering opinions, evaluations, usage patterns, concerns, and benefits) to produce a data-driven view of how the public perceives AI tools.

The output informed a strategic marketing recommendation presented as an executive briefing, complete with visualisations, KPI dashboards, and a phased implementation roadmap.

---

## 🛠️ Tools & Technologies

- **Python** — NLTK, TextBlob, pandas, Matplotlib, Seaborn
- **YouTube Data API** — comment collection
- **Jupyter Notebook** — exploratory analysis

---

## 📊 Key Findings

| Metric | Value |
|--------|-------|
| Overall sentiment | **Positive** |
| Positive comments | 58.3% |
| Neutral comments | 23.1% |
| Negative comments | 18.6% |
| Average sentiment score | +0.247 |
| Query categories analysed | 15 |
| Engagement uplift (positive vs negative) | **2.3×** |

### Top Positive Themes
- Productivity and time-saving benefits
- Creative assistance and content generation
- Educational value and accessibility

### Top Concerns
- Accuracy and factual reliability
- Fear of job displacement
- Over-reliance on AI

---

## 📁 Repository Structure

```
youtube-sentiment-analysis/
├── youtube_sentiment_analysis.py        # Main sentiment analysis script
├── general_chatgpt_sentiment.py         # General sentiment pipeline
├── executive_histograms.py              # KPI histogram visualisations
├── presentation_visualizations.py       # Presentation-ready charts
├── implementation_roadmap_visual.py     # Phased roadmap visualisation
├── requirements.txt                     # Python dependencies
├── FutureProof_Executive_Summary.md     # Full written executive summary
├── FutureProof_Executive_Dashboard.png  # Executive KPI dashboard
├── FutureProof_Business_KPIs.png        # Business KPI breakdown
├── FutureProof_Histogram_Dashboard.png  # Sentiment distribution charts
├── FutureProof_Implementation_Roadmap.png  # Visual roadmap
├── FutureProof_Timeline_Gantt.png       # Gantt chart for implementation
└── README.md
```

---

## 🔑 Strategic Recommendation

**Proceed with AI implementation using a three-phase approach:**

| Phase | Timeline | Focus |
|-------|----------|-------|
| Phase 1 — Controlled Launch | Months 1–2 | Emphasise human oversight, address accuracy concerns |
| Phase 2 — Measured Expansion | Months 3–4 | Case studies, educational content, community engagement |
| Phase 3 — Full Integration | Months 5–6 | Scaled deployment, continuous sentiment monitoring |

---

## ⚙️ How to Run

```bash
pip install -r requirements.txt
python youtube_sentiment_analysis.py
```

To regenerate visualisations:
```bash
python executive_histograms.py
python presentation_visualizations.py
python implementation_roadmap_visual.py
```

---

## 📦 Requirements

```
pandas
nltk
textblob
matplotlib
seaborn
google-api-python-client
```

---

## 📜 Disclaimer

This project was completed as part of a data analytics portfolio. All analysis is for educational and research purposes. "FutureProof" is a fictional organisation used as the business context for this analysis.
