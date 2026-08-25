# Nutrition & Ingredient Verification App

A standalone web app that verifies nutrition
label photos against expected product specs, flagging mismatches by severity.

## What it does

- Upload one or more photos of a Nutrition Facts label
- Enter the expected values (from the supplier's official spec) for each label
- The app extracts values from the photo using a vision LLM and compares them
  against what was entered, classifying each field as:
  - **Match** — values agree
  - **Format Difference** — same real value, different formatting/rounding
    (e.g. "0mg" vs "0 mg")
  - **Critical Failure** — a genuine discrepancy (e.g. spec says 0mg
    cholesterol, label shows 35mg)
  - **Missing** — the field couldn't be reliably read from the photo
- Supports both single-image and batch (multi-image) verification

## Setup

### Prerequisites
- Python 3.10+
- A free Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Installation

```bash
python -m venv venv
source venv/bin/activate      
pip install -r requirements.txt
```

### Configure your API key

Create a `.env` file in the project root:
```
GEMINI_API_KEY= YOUR_API_KEY

```
### Run the app

```bash
streamlit run app.py
```

This opens the app in your browser at `localhost:8501`.


## Tech stack

- **Streamlit** — UI (single-file, all-Python, no separate frontend build)
- **Gemini 3.6 Flash** (`google-genai` SDK) — vision extraction
- **Pydantic** — schema definitions and validation