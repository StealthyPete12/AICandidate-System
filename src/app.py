import streamlit as st
import os
import tempfile
import joblib
import pandas as pd
import re
from collections import Counter

from cv_parser import extract_text_from_cv
from skill_extractor import extract_skills_from_text
from skill_registry import SKILL_REGISTRY

# Map common aliases to a single canonical skill name
SKILL_ALIASES = {
    "amazon web services": "aws",
    "node": "node.js",
    "ci cd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "javascript": "javascript",
    "js": "javascript",
    "reactjs": "react",
}

def normalize_skills(skills):
    normalized = []
    for skill in skills:
        key = skill.lower()
        normalized.append(SKILL_ALIASES.get(key, key))
    return normalized

# Minimum skill signals a CV must have to qualify for each role
ROLE_ELIGIBILITY = {
    "Data Analyst": {"sql", "powerbi", "tableau", "reporting"},
    "Backend Engineer": {"api", "backend", "server", "java", "node.js", "python"},
    "Data Engineer": {"etl", "pipeline", "warehouse", "spark", "airflow", "docker"},
    "DevOps Engineer": {"aws", "azure", "gcp", "docker", "kubernetes", "ci/cd"},
    "ML Engineer": {"machine learning", "model", "training", "pytorch", "tensorflow"},
    "Full Stack Engineer": {"frontend", "backend", "react", "node.js"},
    "Frontend Engineer": {"javascript", "react", "css", "html"},
}


def explain_role_match(extracted_skills: set, role: str):
    """Return the skills that overlap between the CV and a given role."""
    role_skills = SKILL_REGISTRY.get(role, set())
    return sorted(extracted_skills.intersection(role_skills))


# Keywords used to estimate seniority from CV language
SENIORITY_KEYWORDS = {
    "junior": {"intern", "junior", "assist", "trainee"},
    "senior": {"senior", "lead", "principal", "architect", "own", "designed"},
}

def detect_seniority(text: str):
    text = text.lower()
    senior_hits = sum(word in text for word in SENIORITY_KEYWORDS["senior"])
    junior_hits = sum(word in text for word in SENIORITY_KEYWORDS["junior"])

    if senior_hits > junior_hits and senior_hits >= 2:
        return "Senior / Lead level"
    elif junior_hits > senior_hits:
        return "Junior / Entry level"
    else:
        return "Mid‑level"


# --- Streamlit UI ---

st.set_page_config(page_title="AI Candidate Role Matcher", layout="wide")

st.title("🎯 AI Candidate Role Matcher")
st.caption(
    "An ATS‑style role ranking system using eligibility rules, "
    "skill normalization, frequency weighting, and hybrid ML scoring."
)

st.markdown("---")

# Load the trained classifier and skill encoder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")

@st.cache_resource
def load_model():
    model = joblib.load(os.path.join(RESULTS_DIR, "candidate_classifier.pkl"))
    mlb = joblib.load(os.path.join(RESULTS_DIR, "skill_encoder.pkl"))
    return model, mlb

model, mlb = load_model()

uploaded_file = st.file_uploader("Upload your CV (PDF)", type=["pdf"])

if uploaded_file:

    # Extract text from the uploaded CV
    with st.spinner("Analyzing CV…"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        text = extract_text_from_cv(tmp_path)
        raw_skills = extract_skills_from_text(text)
        os.remove(tmp_path)

    if not raw_skills:
        st.error("No recognizable technical skills were found.")
        st.stop()

    # Normalize skills and count how often each appears
    normalized_skills = normalize_skills(raw_skills)
    skill_counts = Counter(normalized_skills)

    extracted_skill_set = set(normalized_skills)

    st.subheader("Extracted Skills (normalized & weighted)")
    for skill, count in skill_counts.items():
        st.write(f"- {skill} (mentions: {count})")

    st.markdown("---")

    seniority_level = detect_seniority(text)
    st.subheader("Seniority Assessment")
    st.write(f"**Estimated level:** {seniority_level}")

    st.markdown("---")

    # Run the ML model to get per-role probabilities
    encoded = mlb.transform([normalized_skills])
    probs = model.predict_proba(encoded)[0]
    roles = model.classes_

    results_df = pd.DataFrame({
        "Role": roles,
        "ML Score": probs
    })

    # Zero out scores for roles the CV isn't eligible for
    def is_role_eligible(role):
        required = ROLE_ELIGIBILITY.get(role, set())
        return bool(extracted_skill_set.intersection(required))

    results_df["Eligible"] = results_df["Role"].apply(is_role_eligible)
    results_df.loc[~results_df["Eligible"], "ML Score"] = 0.0

    # Combine ML probability with skill-overlap into a final score
    def hybrid_score(row):
        role = row["Role"]
        ml_score = row["ML Score"]
        role_skills = SKILL_REGISTRY.get(role, set())

        weighted_overlap = sum(
            skill_counts[s] for s in extracted_skill_set.intersection(role_skills)
        )

        skill_score = weighted_overlap / max(len(role_skills), 1)

        if ml_score > 0:
            return (ml_score * 0.7) + (skill_score * 0.3)
        else:
            return skill_score * 0.5

    results_df["Final Score"] = results_df.apply(hybrid_score, axis=1)

    results_df = results_df.sort_values(
        by="Final Score",
        ascending=False
    ).reset_index(drop=True)

    # Display top 3 roles
    st.subheader("Top 3 Suitable Roles")

    top_3 = results_df.head(3)

    for i, row in top_3.iterrows():
        st.markdown(
            f"""
            **#{i + 1}: {row['Role']}**
            Final Score: `{row['Final Score']:.2f}`
            ML Probability: `{row['ML Score']:.2f}`
            """
        )

    # Explain which skills contributed to each recommendation
    st.subheader("🔍 Why These Roles Appeared")

    for i, row in top_3.iterrows():
        role = row["Role"]
        st.markdown(f"### #{i + 1}: {role}")

        matched = explain_role_match(extracted_skill_set, role)
        if matched:
            st.write("**Supporting skills:**")
            st.write(", ".join(matched))
        else:
            st.write("No strong overlap beyond general technical background.")

    # Bar chart of all role scores
    st.subheader("Role Suitability Ranking")

    chart_df = (
        results_df
        .set_index("Role")[["Final Score"]]
        .sort_values("Final Score")
    )

    st.bar_chart(chart_df)

    # Skill breakdown for the top-ranked role
    st.subheader("🧩 Skill Breakdown (Top Role)")
    top_role = top_3.iloc[0]["Role"]
    top_matches = explain_role_match(extracted_skill_set, top_role)

    if top_matches:
        st.write(", ".join(top_matches))
    else:
        st.write("No dominant skill signals detected.")

    st.markdown("---")
    st.caption(
        "⚠ Prototype ATS-style system. Final hiring decisions "
        "must involve human review."
    )
