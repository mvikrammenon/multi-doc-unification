# Multi-Doc Unification Workflow

This project implements a modular documentation unification workflow using Python and CrewAI.
It processes documentation files for UI components from multiple sources, extracts relevant fields,
aligns them, compares for differences, determines a 'truth' source, and generates a unified
document and a CSV report.

## Project Structure

-   `data/`: Contains source documentation files (e.g., `data/source1/component1.txt`). Mock data is provided.
-   `src/`: Contains the Python source code for the workflow.
    -   `main.py`: Main executable script to run the full pipeline.
    -   `doc_reader.py`: Reads documentation files.
    -   `field_extractor.py`: Extracts fields using a CrewAI agent.
    -   `field_aligner.py`: Aligns fields from multiple sources using a CrewAI agent.
    -   `field_comparer.py`: Compares aligned fields and selects a truth source using a CrewAI agent.
    -   `report_generator.py`: Generates a CSV report of the comparison.
    -   `human_reviewer.py`: Simulates human review and applies decisions.
    -   `doc_generator.py`: Generates the final unified documentation file.
    -   `utils.py`: Utility classes/functions (e.g., `OutputMarkers`).
-   `tests/`: Contains unit tests.
    -   `test_stages.py`: Unit tests for each processing stage. Mock data for tests is defined within the test file or uses the `data/` directory.
-   `output/`: Directory where generated reports and unified documents are saved (created automatically).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Python Environment:**
    Ensure you have Python 3.8+ installed. It's recommended to use a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    The primary dependency is `crewai`. Install it using pip:
    ```bash
    pip install crewai python-dotenv
    ```
    (`python-dotenv` is useful for managing API keys via a `.env` file, though not strictly enforced by the scripts themselves which expect environment variables).

4.  **Environment Variables (Crucial for CrewAI):**
    The CrewAI agents in this project rely on an underlying Large Language Model (LLM) via API (e.g., OpenAI's GPT models). You **MUST** set the required environment variables for CrewAI to function.
    For example, if using OpenAI, you need to set:
    -   `OPENAI_API_KEY`: Your OpenAI API key.
    -   `OPENAI_MODEL_NAME`: (Optional, defaults to a standard model like gpt-4) e.g., `gpt-3.5-turbo` or `gpt-4`.

    You can set these directly in your shell, or create a `.env` file in the project root:
    ```
    OPENAI_API_KEY="your_api_key_here"
    OPENAI_MODEL_NAME="gpt-4"
    ```
    The `main.py` script and individual CrewAI modules will expect these to be available in the environment.

## Running the Workflow

To run the full documentation unification pipeline for a component:

```bash
python src/main.py --component_name <component_name>
```
For example, using the mock data:
```bash
python src/main.py --component_name component1
```
This will:
1.  Read documentation for `component1` from `data/source1`, `data/source2`, etc.
2.  Process the data through all stages (extraction, alignment, comparison).
3.  Generate a CSV report in `output/component1_report.csv`.
4.  Simulate human review (as defined in `main.py`).
5.  Generate a unified documentation file in `output/component1_unified.txt`.

Look for print statements in your console to see the progress and intermediate data structures.

## Running Tests

Unit tests are provided for each processing stage. These tests use mocked CrewAI calls to avoid actual LLM API usage during testing and ensure reproducibility.

To run all tests:
```bash
python -m unittest tests.test_stages
```
You should see output indicating the number of tests run and that all have passed.

---
(Original README content below, for reference on project goals)

# multi-doc-unification
An LLM based modular documentation unification workflow


Implementing a modular documentation unification workflow. Documentation files for each UI component are stored under data/source_name/component_name.txt. Your goal is to extract fields, align them across sources, compare for differences, identify the most accurate or up-to-date information, and output a unified documentation file. Each stage should run as a separate function or module and accept clear input/output data structures. CrewAI and LLM integrations are already configured.

The workflow includes these steps:
	1.	Read all documentation files for a component from the data directory.
	2.	Extract field names, values, required or optional status, and last updated dates from each file into structured data.
  3.	Align and normalize the extracted fields, creating a combined structure with a list of all unique fields, each containing values from every source or a marker if missing.
      Example output: {
        "field1": {
    "source1": { "originalValue": "...", "lastUpdated": "..." },
    "source2": "ENUM.NO_FIELD",
    "source3": { "originalValue": "...", "lastUpdated": "..." }
  },
  ...
}
	4.	Compare the normalized fields, flag differences, assign confidence scores, and select a most likely truth source per field, including rationale.
      Example output: {
        "field1": {
    "diff": {
      "source1": { "modified": true, "value": "...", "confidence": 0.9 },
      "source2": { "modified": false, "value": "ENUM.NO_FIELD", "confidence": 0.7 },
      "source3": { "modified": true, "value": "...", "confidence": 0.95 }
    },
    "truthSource": "source3",
    "explanation": "...",
    "confidenceOverall": 0.92
  },
  ...
}
	5.	Present a report of aligned fields, differences, truth source, and confidence, clearly highlighting fields that need human review - table format in csv.
	6.	Accept human decisions on flagged fields and update the data structure accordingly.
	7.	Generate a unified documentation file from the final, reviewed field data.

Example input data locations:

data/source1/component1.txt
data/source2/component1.txt
data/source3/component1.txt

Example of normalized structure for a field:

field1:
source1: { value: …, required: true, lastUpdated: … }
source2: { value: …, required: false, lastUpdated: … }
source3: NO_FIELD

Each function or module should accept and return structured data, and stages must be runnable independently for debugging and pipeline automation.
