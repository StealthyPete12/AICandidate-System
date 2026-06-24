import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(RESULTS_DIR, exist_ok=True)

# Load training data
df = pd.read_csv(os.path.join(DATA_DIR, "sample_candidates.csv"))
df["skills"] = df["skills"].apply(lambda x: x.split(","))

# Encode skills as binary features
mlb = MultiLabelBinarizer()
X = pd.DataFrame(mlb.fit_transform(df["skills"]), columns=mlb.classes_)
y = df["target_role"]

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

# Train a decision tree classifier
model = DecisionTreeClassifier(
    max_depth=5,
    criterion="gini",
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate on the test set
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

# Save the model, encoder, and evaluation report
joblib.dump(model, os.path.join(RESULTS_DIR, "candidate_classifier.pkl"))
joblib.dump(mlb, os.path.join(RESULTS_DIR, "skill_encoder.pkl"))

with open(os.path.join(RESULTS_DIR, "classification_report.txt"), "w") as f:
    f.write(f"Accuracy: {accuracy:.3f}\n\n")
    f.write(report)

print("Training complete")
print(f"Accuracy: {accuracy:.3f}")
