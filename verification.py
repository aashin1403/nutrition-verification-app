from models import ExpectedSpec, ExtractedLabel, FieldResult

def check_field(expected_value: float, extracted_value: float | None, confidence: float) -> str:
    if extracted_value is None or confidence < 0.6:
        return "missing"

    diff = abs(expected_value - extracted_value)

    if diff < 0.1 :
        return "match"
    elif diff <= 2.0 :
        return "format_difference"
    else: 
        return "critical_failure"

def compare(expected: ExpectedSpec, extracted: ExtractedLabel) -> list[FieldResult]:
    results = []
    #Numeric fields
    numeric_fields = ["total_fat_g", "cholesterol_mg", "sodium_mg"]
    for field_name in numeric_fields:
        expected_val = getattr(expected, field_name)
        reading = getattr(extracted, field_name)  # a FieldReading

        status = check_field(expected_val, reading.value, reading.confidence)

        results.append(FieldResult(
            field_name=field_name,
            expected_value=str(expected_val),
            extracted_value=str(reading.value),
            status=status,
        ))


    # Brand name field
    text_fields = ["brand_name", "serving_size"]
    for field_name in text_fields:
        expected_val = getattr(expected, field_name).strip().lower()
        reading = getattr(extracted, field_name)

        if reading.value is None or reading.confidence < 0.6:
            status = "missing"
        elif str(reading.value).strip().lower() == expected_val:
            status = "match"
        else:
            status = "critical_failure"

        results.append(FieldResult(
            field_name=field_name,
            expected_value=getattr(expected, field_name),
            extracted_value=str(reading.value),
            status=status,
        ))

    # Allergens field
    expected_set = set(a.strip().lower() for a in expected.allergens)
    extracted_set = set(a.strip().lower() for a in extracted.allergens)

    if expected_set == extracted_set:
        allergen_status = "match"
    elif expected_set - extracted_set:
        # label is missing an allergen that the spec says should be there **always critical
        allergen_status = "critical_failure"
    else:
        # extracted has extra allergens not in the spec (flagged)
        allergen_status = "format_difference"

    results.append(FieldResult(
        field_name="allergens",
        expected_value=", ".join(expected.allergens),
        extracted_value=", ".join(extracted.allergens),
        status=allergen_status,
    ))

    return results