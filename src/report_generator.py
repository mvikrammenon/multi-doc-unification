import csv
import json
from src.utils import OutputMarkers # Not strictly needed for writing, but good for context

def generate_csv_report(evaluated_data: dict, output_csv_path: str, review_threshold: float = 0.9) -> None:
    """
    Generates a CSV report from evaluated field data.

    Args:
        evaluated_data: Dictionary output from field_comparer.py.
        output_csv_path: File path for the output CSV.
        review_threshold: Confidence score below which a field is marked for review.
    """
    header = [
        "FieldName", "TruthSource", "TruthValue", "TruthIsRequired",
        "TruthLastUpdated", "OverallConfidence", "NeedsReview", "AllSourcesDetailsJSON"
    ]

    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for field_name, field_info in evaluated_data.items():
            truth_source = field_info.get('truthSource')
            overall_confidence = field_info.get('confidenceOverall', 0.0)

            truth_value = "N/A"
            truth_is_required = "N/A"
            truth_last_updated = "N/A"

            if truth_source and truth_source in field_info.get('diff', {}):
                truth_details = field_info['diff'][truth_source]
                # Check if truth_details is not a string (like "ENUM.NO_FIELD")
                if isinstance(truth_details, dict):
                    truth_value = truth_details.get('value', "N/A")
                    truth_is_required = truth_details.get('isRequired', 'N/A')
                    truth_last_updated = truth_details.get('lastUpdated', 'N/A')
                else: # Handles case where truth_source points to an "ENUM.NO_FIELD" string
                    truth_value = str(truth_details) # Should be "ENUM.NO_FIELD"
            elif truth_source == "NO_TRUTH_SOURCE_FOUND": # Explicit check for this marker
                 pass # Defaults N/A are already set

            # NeedsReview logic:
            # True if confidenceOverall < review_threshold OR if truthSource is missing/not found
            needs_review = (overall_confidence < review_threshold) or \
                           (truth_source == "NO_TRUTH_SOURCE_FOUND") or \
                           (truth_source is None)
            
            # More advanced discrepancy check (optional for now, as per instructions)
            # if not needs_review and isinstance(field_info.get('diff'), dict):
            #     source_values = []
            #     for source_data in field_info['diff'].values():
            #         if isinstance(source_data, dict) and 'value' in source_data:
            #             if source_data['value'] != str(OutputMarkers.NO_FIELD):
            #                 source_values.append(source_data['value'])
            #     if len(set(source_values)) > 1: # More than one unique value exists
            #         needs_review = True


            all_sources_details_json = json.dumps(field_info.get('diff', {}))

            row = [
                field_name,
                truth_source if truth_source is not None else "N/A",
                truth_value,
                str(truth_is_required), # Ensure boolean is converted to string
                truth_last_updated,
                str(overall_confidence), # Ensure float is converted to string
                str(needs_review), # Ensure boolean is converted to string
                all_sources_details_json
            ]
            writer.writerow(row)
