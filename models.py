from pydantic import BaseModel

class ExpectedSpec(BaseModel):
    brand_name: str
    serving_size: float
    total_fat_g: float
    cholesterol_mg: float
    sodium_mg: float
    allergens: list[str]

class FieldReading(BaseModel):
    value: float | str | None       
    confidence: float          # 0.0 to 1.0
    raw_text: str | None       

class ExtractedLabel(BaseModel):
    serving_size: FieldReading
    total_fat_g: FieldReading
    cholesterol_mg: FieldReading
    sodium_mg: FieldReading
    allergens: list[str]

class FieldResult(BaseModel):
    field_name: str
    expected_value: str
    extracted_value: str | None
    status: str
    note: str | None = None


def failed_extraction() -> ExtractedLabel:
    # Values if extraction fails completely. All fields are missing, and confidence is 0.0.
    empty_reading = FieldReading(value=None, confidence=0.0, raw_text=None)
    return ExtractedLabel(
        serving_size=empty_reading,
        total_fat_g=empty_reading,
        cholesterol_mg=empty_reading,
        sodium_mg=empty_reading,
        allergens=[],
    )