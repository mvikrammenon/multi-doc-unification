from src.utils import OutputMarkers

def generate_unified_document(final_reviewed_data: dict, output_doc_path: str) -> None:
    """
    Generates a unified document from the final reviewed field data.

    Args:
        final_reviewed_data: Dictionary output from human_reviewer.py (or field_comparer.py).
                             Keys are field names.
        output_doc_path: The file path where the unified document should be saved.
    """
    with open(output_doc_path, 'w') as f:
        for field_name, field_info in final_reviewed_data.items():
            truth_source_name = field_info.get('truthSource')

            if not truth_source_name or truth_source_name == "NO_TRUTH_SOURCE_FOUND":
                continue

            truth_details = field_info.get('diff', {}).get(truth_source_name)

            if not truth_details or not isinstance(truth_details, dict) or \
               truth_details.get('value') == str(OutputMarkers.NO_FIELD):
                continue

            value = truth_details['value']
            # Ensure isRequired is a string ("True"/"False") or "N/A"
            is_required_raw = truth_details.get('isRequired', 'N/A')
            if isinstance(is_required_raw, bool):
                is_required = str(is_required_raw)
            else:
                is_required = str(is_required_raw) # Handles "N/A" or any other string representation

            last_updated = truth_details.get('lastUpdated', 'N/A')

            f.write(f"Field: {field_name}\n")
            f.write(f"Value: {value}\n")
            f.write(f"Required: {is_required}\n")
            f.write(f"Last Updated: {last_updated}\n\n")
