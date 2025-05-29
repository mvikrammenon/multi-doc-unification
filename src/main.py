import argparse
import json
import os

from src.doc_reader import read_component_docs
from src.field_extractor import extract_fields_from_content
from src.field_aligner import align_and_normalize_fields
from src.field_comparer import compare_and_evaluate_fields
from src.report_generator import generate_csv_report
from src.human_reviewer import apply_human_decisions
from src.doc_generator import generate_unified_document
# from src.utils import OutputMarkers # Not directly used in main, but good for context

def main():
    parser = argparse.ArgumentParser(description="Process component documentation.")
    parser.add_argument("--component_name", type=str, required=True,
                        help="Name of the component to process (e.g., component1)")
    args = parser.parse_args()
    component_name = args.component_name

    print(f"Starting documentation processing workflow for: {component_name}\n")

    # Stage 1: Read Documentation
    print("--- Stage 1: Reading Documentation ---")
    docs_by_source = read_component_docs(component_name)
    if not docs_by_source:
        print(f"No documentation found for component '{component_name}'. Exiting.")
        return
    print(f"Found documentation from {len(docs_by_source)} sources: {list(docs_by_source.keys())}\n")

    # Stage 2: Extract Fields
    print("--- Stage 2: Extracting Fields ---")
    extracted_data_by_source: dict[str, list[dict]] = {}
    for source_name, doc_content in docs_by_source.items():
        print(f"Extracting fields from {source_name} for {component_name}...")
        try:
            # Note: OPENAI_API_KEY (or other LLM provider keys) must be set in the environment
            # if the CrewAI tasks are not mocked and are intended to run live.
            extracted_data_by_source[source_name] = extract_fields_from_content(doc_content)
            print(f"Successfully extracted {len(extracted_data_by_source[source_name])} fields from {source_name}.")
        except Exception as e:
            print(f"Error extracting fields from {source_name}: {e}")
            extracted_data_by_source[source_name] = [] # Store empty list on error
    print("\nExtracted data by source:")
    print(json.dumps(extracted_data_by_source, indent=2))
    print("-" * 30 + "\n")

    # Stage 3: Align Fields
    print("--- Stage 3: Aligning Fields ---")
    # Ensure there's some data to align
    if not any(extracted_data_by_source.values()):
        print("No fields were extracted from any source. Cannot proceed with alignment. Exiting.")
        return
        
    aligned_fields = align_and_normalize_fields(extracted_data_by_source)
    print("\nAligned fields:")
    print(json.dumps(aligned_fields, indent=2))
    print("-" * 30 + "\n")

    # Stage 4: Compare and Evaluate Fields
    print("--- Stage 4: Comparing and Evaluating Fields ---")
    if not aligned_fields:
        print("No aligned fields to compare. Exiting.")
        return
    evaluated_data = compare_and_evaluate_fields(aligned_fields)
    print("\nEvaluated data:")
    print(json.dumps(evaluated_data, indent=2))
    print("-" * 30 + "\n")

    # Stage 5: Generate CSV Report
    print("--- Stage 5: Generating CSV Report ---")
    os.makedirs("output", exist_ok=True)
    report_path = os.path.join("output", f"{component_name}_report.csv")
    print(f"Generating CSV report to {report_path}...")
    generate_csv_report(evaluated_data, report_path)
    print(f"CSV report generated: {report_path}\n")

    # Stage 6: Apply Human Decisions (Simulated)
    print("--- Stage 6: Simulating Human Review ---")
    mock_human_decisions = {}
    if "Version" in evaluated_data and "source1" in evaluated_data["Version"]["diff"]:
        mock_human_decisions["Version"] = {
            "chosenSource": "source1",
        }
        print("Simulating human decision for 'Version' field to use 'source1'.")
    elif "Title" in evaluated_data : # Fallback if Version isn't there, just to show manual input
         mock_human_decisions["Title"] = {
            "chosenSource": "MANUAL_INPUT",
            "manualValue": "Manually Set Title",
            "manualIsRequired": True,
            "manualLastUpdated": "2024-03-15"
        }
         print("Simulating human decision for 'Title' field with MANUAL_INPUT.")
    else:
        print("No specific fields like 'Version' or 'Title' found for mock human review in this run.")


    if mock_human_decisions:
        final_data = apply_human_decisions(evaluated_data, mock_human_decisions)
        print("\nHuman decisions applied. Final data after review:")
        print(json.dumps(final_data, indent=2))
    else:
        final_data = evaluated_data
        print("No mock human decisions applied for this run.")
    print("-" * 30 + "\n")

    # Stage 7: Generate Unified Document
    print("--- Stage 7: Generating Unified Document ---")
    unified_doc_path = os.path.join("output", f"{component_name}_unified.txt")
    print(f"Generating unified document to {unified_doc_path}...")
    generate_unified_document(final_data, unified_doc_path)
    print(f"Unified document generated: {unified_doc_path}\n")

    print("--- Workflow completed! ---")

if __name__ == "__main__":
    # Reminder: For CrewAI tasks to run (field_extractor, field_aligner, field_comparer),
    # ensure necessary API keys (e.g., OPENAI_API_KEY) and environment variables are set.
    # The tests for individual modules used mocking, so this main script might be the
    # first place they run "live" or require actual API access if not configured for local models.
    main()
