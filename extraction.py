import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from models import ExtractedLabel, failed_extraction
import json
import time

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = """
Analyze this nutrition facts label image and extract the following fields.
Return ONLY valid JSON, no markdown formatting, no explanation, no code fences.

For each field, provide:
- value: the extracted value (or null if unreadable)
- confidence: a number from 0.0 to 1.0 representing how certain you are
- raw_text: the exact text you read for this field (or null if unreadable)

For serving_size specifically: always convert and report the value in grams (g),
even if the label shows it in ounces or another unit. Include the original label
text in raw_text for reference.

If it is NOT a nutrition facts label, return exactly:
{"is_nutrition_label": false}

If it IS a nutrition facts label, extract the following fields and return:
{
  "is_nutrition_label": true,
  "serving_size": {"value": <number in grams>, "confidence": ..., "raw_text": "..."},
  "total_fat_g": {"value": ..., "confidence": ..., "raw_text": ...},
  "cholesterol_mg": {"value": ..., "confidence": ..., "raw_text": ...},
  "sodium_mg": {"value": ..., "confidence": ..., "raw_text": ...},
  "allergens": ["list", "of", "allergen", "strings"]
}

Return ONLY valid JSON, no markdown formatting, no explanation, no code fences.
"""

def parse_gemini_response(raw_text: str) -> ExtractedLabel | None:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini response was not valid JSON: {e}") from e

    if not data.get("is_nutrition_label", False):
        return None

    try:
        return ExtractedLabel(**{k: v for k, v in data.items() if k != "is_nutrition_label"})
    except Exception as e:
        raise ValueError(f"Gemini JSON did not match expected schema: {e}") from e


def extract_label(image_bytes: bytes, max_retries: int = 2) -> ExtractedLabel | None:
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    last_error = None

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt, image_part]
            )
            return parse_gemini_response(response.text)
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(1.5 * (attempt + 1))
                continue

    print(f"extract_label failed after {max_retries + 1} attempts: {last_error}")
    return failed_extraction()