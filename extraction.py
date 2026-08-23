import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from models import ExtractedLabel, FieldReading
import json

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open("data/images.jpg", "rb") as f:
    image_bytes = f.read()

image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

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

Return this exact JSON structure:
{
  "serving_size": {"value": ..., "confidence": ..., "raw_text": ...},
  "total_fat_g": {"value": ..., "confidence": ..., "raw_text": ...},
  "cholesterol_mg": {"value": ..., "confidence": ..., "raw_text": ...},
  "sodium_mg": {"value": ..., "confidence": ..., "raw_text": ...},
  "allergens": ["list", "of", "allergen", "strings"]
}
"""

def parse_gemini_response(raw_text: str) -> ExtractedLabel:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    data = json.loads(cleaned)
    return ExtractedLabel(**data)

def extract_label(image_bytes: bytes) -> ExtractedLabel:
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[prompt, image_part]
    )

    return parse_gemini_response(response.text)