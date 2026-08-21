from pydantic import BaseModel

class ExpectedSpec(BaseModel):
    brand_name: str
    serving_size: str
    total_fat_g: float
    cholesterol_mg: float
    sodium_mg: float
    allergens: list[str]

class FieldReading(BaseModel):
    value: float | str | None       
    confidence: float          # 0.0 to 1.0
    raw_text: str | None       

class ExtractedLabel(BaseModel):
    brand_name: FieldReading
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
