# Quick test to verify text extraction from a sample CV
from cv_parser import extract_text_from_cv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CV_PATH = os.path.join(BASE_DIR, "data", "my_cv.pdf")

print("CV path being tested:")
print(CV_PATH)

# Extract and print the first 1000 chars as a sanity check
text = extract_text_from_cv(CV_PATH)

print("==== EXTRACTED TEXT ====")
print(text[:1000])