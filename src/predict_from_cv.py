import os
import joblib
import numpy as np

from cv_parser import extract_text_from_cv
from skill_extractor import extract_skills_from_text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CV_PATH = os.path.join(BASE_DIR, "data", "my_cv.pdf")
MODEL_PATH = os.path.join(BASE_DIR, "results", "candidate_classifier.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "results", "skill_encoder.pkl")

# Load the trained model and skill encoder
model = joblib.load(MODEL_PATH)
mlb = joblib.load(ENCODER_PATH)

# Extract text and skills from the CV
text = extract_text_from_cv(CV_PATH)
skills = extract_skills_from_text(text)

# Predict the best-fit role and its confidence
encoded = mlb.transform([skills])
prediction = model.predict(encoded)[0]
confidence = float(np.max(model.predict_proba(encoded)[0]))

print("==== AI CLASSIFICATION RESULT ====")
print({
    "extracted_skills": skills,
    "predicted_role": prediction,
    "confidence_score": round(confidence, 3)
})
