import streamlit as st
from models import ExpectedSpec
from extraction import extract_label
from verification import compare

st.title("Nutrition Label Verification")

uploaded_files = st.file_uploader(
    "Upload nutrition label(s)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

STATUS_STYLE = {
    "match": ("✅", "green"),
    "format_difference": ("⚠️", "orange"),
    "critical_failure": ("❌", "red"),
    "missing": ("❓", "gray"),
}

if uploaded_files:
    st.subheader("Enter expected spec for each label")

    single_upload = len(uploaded_files) == 1

    for i, file in enumerate(uploaded_files):
        with st.expander(f"📄 {file.name}", expanded=single_upload):
            st.image(file, width=200)
            st.text_input("Brand Name", key=f"brand_{i}")
            st.text_input("Serving Size (e.g. 30g)", key=f"serving_{i}")
            st.number_input("Total Fat (g)", min_value=0.0, key=f"fat_{i}")
            st.number_input("Cholesterol (mg)", min_value=0.0, key=f"chol_{i}")
            st.number_input("Sodium (mg)", min_value=0.0, key=f"sodium_{i}")
            st.text_input("Allergens (comma-separated)", key=f"allergens_{i}")

    if st.button("Verify All"):
        st.session_state["batch_results"] = []

        for i, file in enumerate(uploaded_files):
            expected = ExpectedSpec(
                brand_name=st.session_state[f"brand_{i}"],
                serving_size=st.session_state[f"serving_{i}"],
                total_fat_g=st.session_state[f"fat_{i}"],
                cholesterol_mg=st.session_state[f"chol_{i}"],
                sodium_mg=st.session_state[f"sodium_{i}"],
                allergens=[a.strip() for a in st.session_state[f"allergens_{i}"].split(",") if a.strip()],
            )

            with st.spinner(f"Analyzing {file.name}..."):
                extracted = extract_label(file.getvalue())

            if extracted is None:
                st.session_state["batch_results"].append({
                    "filename": file.name,
                    "not_a_label": True,
                    "results": None,
                })
            else:
                results = compare(expected, extracted)
                st.session_state["batch_results"].append({
                    "filename": file.name,
                    "not_a_label": False,
                    "results": results,
                })

if "batch_results" in st.session_state:
    st.subheader("Results Summary")

    summary_rows = []
    for item in st.session_state["batch_results"]:
        if item["not_a_label"]:
            summary_rows.append((item["filename"], "🚫 Not a label", "—"))
        else:
            critical_count = sum(1 for r in item["results"] if r.status == "critical_failure")
            overall = "❌ Critical" if critical_count > 0 else "✅ Pass"
            summary_rows.append((item["filename"], overall, f"{critical_count} critical"))

    for filename, overall, detail in summary_rows:
        st.markdown(f"**{filename}** — {overall} ({detail})")

    st.divider()
    st.subheader("Detailed Results")

    single_result = len(st.session_state["batch_results"]) == 1

    for item in st.session_state["batch_results"]:
        with st.expander(f"Details: {item['filename']}", expanded=single_result):
            if item["not_a_label"]:
                st.error("🚫 This doesn't appear to be a nutrition facts label. Please upload a clear photo of the label.")
            else:
                for r in item["results"]:
                    icon, color = STATUS_STYLE.get(r.status, ("❓", "gray"))
                    status_label = r.status.replace("_", " ").title()

                    confidence_line = ""
                    if r.status == "format_difference" and r.confidence is not None:
                        confidence_line = f"Confidence: `{r.confidence:.0%}`  \n"

                    st.markdown(
                        f"{icon} **{r.field_name}**  \n"
                        f"Expected: `{r.expected_value}`  \n"
                        f"Extracted: `{r.extracted_value}`  \n"
                        f"{confidence_line}"
                        f"Status: :{color}[**{status_label}**]"
                    )
                    st.divider()