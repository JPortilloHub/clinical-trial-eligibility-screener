# Clinical Trial Eligibility Screener

An AI-powered system that analyzes patient electronic health records (EHR) against clinical trial inclusion/exclusion criteria to determine eligibility. Built with Claude AI, vector embeddings, and a Streamlit dashboard for visualization.

## Overview

This tool automates the patient screening process for clinical trials by:

1. **Extracting eligibility criteria** from clinical trial protocol PDFs using Claude AI
2. **Embedding criteria** into a vector database (ChromaDB) for semantic search
3. **Analyzing patient records** against criteria using structured AI assessment
4. **Visualizing results** through an interactive Streamlit dashboard

## Features

- **PDF Protocol Parsing**: Automatically extracts inclusion/exclusion criteria from clinical trial protocols
- **TOON Format Conversion**: Converts patient CSV data to Token-Oriented Object Notation for efficient token usage
- **Structured AI Assessment**: Uses Claude's tool use capability for consistent, structured eligibility outputs
- **Vector Database Storage**: Enables semantic search across multiple trial protocols (via Voyage AI + ChromaDB)
- **Interactive Dashboard**: Real-time filtering, visualizations, and export capabilities

## Project Structure

```
clinical-trial-eligibility-screener/
├── elgibility-screener.py      # Main screening script
├── dashboard.py                 # Streamlit dashboard
├── clinical-trial-protocol.pdf  # Sample clinical trial protocol
├── eligibility_results.json     # Generated screening results
├── environment.yml              # Conda environment configuration
├── patients/                    # Patient EHR data (CSV files)
│   ├── EHR_001.csv
│   ├── EHR_002.csv
│   └── ...
└── README.md
```

## Prerequisites

- Python 3.12+
- [Anthropic API key](https://console.anthropic.com/)
- [Voyage AI API key](https://www.voyageai.com/) (for embeddings)

## Installation

### Option 1: Using Conda (Recommended)

```bash
# Clone the repository
git clone https://github.com/JPortilloHub/clinical-trial-eligibility-screener.git
cd clinical-trial-eligibility-screener

# Create and activate the conda environment
conda env create -f environment.yml
conda activate eligibility-screener-env
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/JPortilloHub/clinical-trial-eligibility-screener.git
cd clinical-trial-eligibility-screener

# Install dependencies
pip install anthropic pypdf langchain_voyageai langchain_chroma streamlit pandas plotly openpyxl
```

## Configuration

Set your API keys as environment variables:

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export VOYAGE_API_KEY="your-voyage-api-key"
```

## Usage

### 1. Run the Eligibility Screener

Process all patient records in the `patients/` folder:

```bash
python elgibility-screener.py
```

This will:
- Parse the clinical trial protocol PDF
- Extract eligibility criteria using Claude Haiku
- Convert each patient CSV to TOON format
- Assess eligibility using Claude Sonnet
- Save results to `eligibility_results.json`

### 2. Launch the Dashboard

View and analyze results in the interactive dashboard:

```bash
streamlit run dashboard.py
```

The dashboard provides three main views:

| Tab | Description |
|-----|-------------|
| **Overview** | KPI cards, eligibility distribution chart, confidence scores by patient |
| **Patient Details** | Individual patient assessment with criteria breakdown and recommendations |
| **Full Report** | Summary table with export options (Excel, CSV, Email) |

## Patient Data Format

Patient records should be CSV files with the following sections:

```csv
PATIENT DEMOGRAPHICS
Field,Value
"name","Patient 001"
"age","68"
"sex","Male"
...

VITAL SIGNS
Measurement,Value,Date
"bp","130/80 mmHg","01/03/2026"
...

MEDICATIONS
Medication,Dose,Route,Frequency,Indication,Prescriber
"Donepezil","10mg","Oral","Once daily","AD","Dr. Neurologist"
...

LABORATORY RESULTS
Test,Value,Reference Range,Date,Flag
"MMSE","24","24-30","01/03/2026","Normal"
...
```

## Eligibility Assessment Output

Each patient assessment includes:

| Field | Description |
|-------|-------------|
| `patient_id` | Patient identifier |
| `overall_eligibility` | `ELIGIBLE`, `NOT_ELIGIBLE`, `LIKELY_ELIGIBLE`, or `UNCLEAR` |
| `confidence_score` | 0.0 - 1.0 confidence in the assessment |
| `criteria_evaluation` | Array of individual criteria with status (`MET`, `NOT_MET`, `NEEDS_VERIFICATION`) |
| `recommendation` | Clinical recommendation summary |
| `next_steps` | Suggested follow-up actions |

## Dashboard Features

### Filters
- Filter by eligibility status (Eligible, Not Eligible, Likely Eligible, Unclear)
- Filter by confidence threshold (0-100%)
- Filters sync across all tabs

### Visualizations
- Eligibility distribution pie chart
- Confidence scores bar chart
- Criteria evaluation table with color coding

### Export Options
- Download Excel report (multi-sheet)
- Download CSV summary
- Send via email

## Technologies Used

- **[Claude AI](https://anthropic.com)**: Haiku for extraction, Sonnet for assessment
- **[Voyage AI](https://voyageai.com)**: Text embeddings (voyage-3 model)
- **[ChromaDB](https://www.trychroma.com)**: Vector database for criteria storage
- **[Streamlit](https://streamlit.io)**: Interactive dashboard framework
- **[Plotly](https://plotly.com)**: Data visualizations
- **[pypdf](https://pypdf.readthedocs.io)**: PDF text extraction

## License

This project is for educational and research purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
