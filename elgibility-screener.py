#!git clone https://github.com/JPortilloHub/clinical-trial-eligibility-screener.git
import anthropic
from pypdf import PdfReader
from langchain_voyageai import VoyageAIEmbeddings
from langchain_chroma import Chroma
import os
import glob
import csv
import json

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

#1. Read clinical protocol and save it in a string
file_path = "clinical-trial-protocol.pdf"
reader = PdfReader(file_path)
clinical_trial_protocol = ""
for page in reader.pages:
    clinical_trial_protocol += page.extract_text()

#2. and extract the part you are interested in: Eligibility criteria
extraction_prompt= f"""" You are a a clinician, and your task is to extract the section Patient Selection Criteria, 
including Inclusion Criteria and Exclusion Criteria from the document in pdf wihtin curly brackets. 
Return only the text of that section

<document>
{clinical_trial_protocol}
</document>
"""

response = client.messages.create(
    model = "claude-haiku-4-5-20251001",
    max_tokens = 2000,
    messages = [{"role": "user", "content": extraction_prompt}]
)

eligibility_criteria_extraction = response.content[0].text


#(optional)3 Embed the eligibility criteria into the vector database in case of having several protocols
eligibility_criteria_embedded = VoyageAIEmbeddings(model="voyage-3", voyage_api_key=os.environ.get("VOYAGE_API_KEY"))

eligibility_criteria_vector_db = Chroma.from_texts(
    texts=[eligibility_criteria_extraction],
    embedding=eligibility_criteria_embedded,
    collection_name="eligibility_criteria",
    metadatas=[{"source": "clinical-trial-protocol.pdf", "section": "Patient Selection Criteria"}]
)


#4 Define how to convert csv to TOON format. This way it consumes less tokens
def csv_to_toon(file_path):
    """Convert a patient CSV file to TOON (Token-Oriented Object Notation) format."""
    result = {}
    current_section = None
    current_headers = None

    with open(file_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or all(cell.strip() == "" for cell in row):
                continue

            # Check if this is a section header (single cell that is all uppercase words)
            # Section headers are like "PATIENT DEMOGRAPHICS", "VITAL SIGNS", "LABORATORY RESULTS"
            first_cell = row[0].strip()
            is_section_header = (
                len(row) == 1 and
                first_cell.isupper() and
                all(word.isupper() for word in first_cell.split())
            )
            if is_section_header:
                current_section = first_cell.replace(" ", "_")
                result[current_section] = {"headers": None, "rows": []}
                current_headers = None
                continue

            # If we don't have headers yet, this row is the header
            if current_section and current_headers is None:
                current_headers = [h.strip() for h in row]
                result[current_section]["headers"] = current_headers
                continue

            # Data row - store as list of values, padded to match header count
            if current_section and current_headers:
                row_values = [value.strip() for value in row]
                # Pad row to match header count if needed
                while len(row_values) < len(current_headers):
                    row_values.append("")
                # Trim row if it has more values than headers
                row_values = row_values[:len(current_headers)]
                result[current_section]["rows"].append(row_values)

    # Convert to TOON format string
    toon_lines = []
    for section, data in result.items():
        headers = data["headers"]
        rows = data["rows"]
        if headers and rows:
            # TOON tabular format: section[count]{fields}:
            header_str = ",".join(headers)
            toon_lines.append(f"{section}[{len(rows)}]{{{header_str}}}:")
            for row in rows:
                # Ensure row has exactly the same number of fields as headers
                toon_lines.append(f"  {','.join(row)}")
        toon_lines.append("")  # Empty line between sections

    return "\n".join(toon_lines)



#5 Define the tool schema for structured output
tools = [
    {
        "name": "record_eligibility_assessment",
        "description": "Record the patient eligibility assessment for a clinical trial",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {"type": "string"},
                "trial_id": {"type": "string"},
                "overall_eligibility": {
                    "type": "string",
                    "enum": ["ELIGIBLE", "NOT_ELIGIBLE", "LIKELY_ELIGIBLE", "UNCLEAR"]
                },
                "confidence_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "criteria_evaluation": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "criterion": {"type": "string"},
                            "patient_value": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["MET", "NOT_MET", "NEEDS_VERIFICATION"]
                            },
                            "score": {"type": "number"}
                        },
                        "required": ["criterion", "status", "score"]
                    }
                },
                "recommendation": {"type": "string"},
                "next_steps": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["patient_id", "trial_id", "overall_eligibility", "confidence_score"]
        }
    }
]

def assess_patient_eligibility(patient_id, patient_toon, eligibility_criteria):
    """Assess a single patient's eligibility for the clinical trial."""
    prompt = f"""
Analyze the patient's eligibility for the clinical trial based on their data and the eligibility criteria.

<patientid>
{patient_id}
</patientid>

<patientdata>
{patient_toon}
</patientdata>

<trialeligibilitycriteria>
{eligibility_criteria}
</trialeligibilitycriteria>

Use the record_eligibility_assessment tool to record your assessment.
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        tools=tools,
        tool_choice={"type": "tool", "name": "record_eligibility_assessment"},
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract the tool use response
    for block in response.content:
        if block.type == "tool_use":
            return block.input

    return None

#6 Main: Read all patient CSV files and assess eligibility
if __name__ == "__main__":
    patients_folder = "patients"
    patient_files = sorted(glob.glob(os.path.join(patients_folder, "*.csv")))

    # Store all eligibility results
    all_results = []

    print(f"Processing {len(patient_files)} patients...")

    for patient_file in patient_files:
        patient_id = os.path.basename(patient_file).replace(".csv", "")
        patient_toon = csv_to_toon(patient_file)

        print(f"Assessing {patient_id}...")

        result = assess_patient_eligibility(
            patient_id,
            patient_toon,
            eligibility_criteria_extraction
        )

        if result:
            all_results.append(result)
            print(f"  -> {result.get('overall_eligibility', 'UNKNOWN')} (confidence: {result.get('confidence_score', 0):.2f})")

    # Save results to JSON file for the dashboard
    output_file = "eligibility_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to {output_file}")



