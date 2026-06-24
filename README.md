# AI Candidate Role Matcher

An ATS-style application that analyzes a CV and ranks the top 3 most suitable technical roles using eligibility rules, skill normalization, and ML-assisted scoring.

**[Try the live demo](https://ai-candidate-system-1-34hyurh2hevdqdtzqtsjgl.streamlit.app/)**

---

## What It Does

Upload a CV (PDF or DOCX) and get back a ranked list of the **top 3 matching roles**, each with a score and an explanation of why it was chosen.

Most job-matching demos use a single ML prediction to pick one role. In reality:

- One CV can match multiple roles
- Some roles should be excluded when core requirements are missing
- ML should inform the decision, not make it alone
- Results need to be ranked and explained

---

## Architecture

<p align="center">
  <img src="docs/architecture.svg" alt="System Architecture" width="820"/>
</p>

---

## How It Works

### 1. Skill Extraction & Normalization

Skills are pulled from the CV text and normalized against a central registry. Aliases like "JS" and "JavaScript" map to the same skill. Skills mentioned multiple times carry more weight — this helps separate real experience from keyword stuffing.

### 2. Eligibility Gating

Each role defines must-have signals (e.g. Data Analyst requires SQL + BI tools, DevOps requires cloud + containers). If none of those signals are present, the role is excluded — no matter how confident the ML model is. This cuts down on false positives.

### 3. Hybrid Scoring (ML + Skills)

ML probability is combined with a skill-overlap score:

- **High ML confidence** — ML contributes 70%, skill overlap 30%
- **Low/zero ML confidence** — skill overlap provides a fallback at 50% weight

This handles hybrid and uncommon profiles that the training data may not cover well.

### 4. Seniority Detection

A lightweight keyword scan estimates Junior / Mid / Senior level based on responsibility language, experience indicators, and leadership signals.

---

## Tech Stack

| Component | Library |
|---|---|
| UI & Deployment | Streamlit |
| ML Model | scikit-learn (Decision Tree) |
| Model Persistence | joblib |
| CV Parsing | pdfplumber, python-docx |
| Data Processing | pandas, numpy |

---

## Limitations

- Training dataset is intentionally small and illustrative
- Skill extraction is rule-based and relies on a fixed skill list
- Eligibility rules and scoring weights are approximate

---

## Summary

This is a decision-support system, not a job-title predictor. It filters out irrelevant roles, ranks the plausible ones, and explains every recommendation.
