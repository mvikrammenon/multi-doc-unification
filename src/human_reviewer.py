import json
from src.utils import OutputMarkers

def apply_human_decisions(evaluated_data: dict, human_decisions: dict) -> dict:
    """
    Applies human reviewer decisions to the evaluated field data.

    Args:
        evaluated_data: The dictionary output from field_comparer.py.
        human_decisions: A dictionary of human overrides.

    Returns:
        The modified evaluated_data dictionary.
    """
    for field_name, decision in human_decisions.items():
        if field_name in evaluated_data:
            field_entry = evaluated_data[field_name]
            chosen_source = decision.get('chosenSource')

            if not chosen_source: # Skip if no chosenSource is provided
                continue

            if chosen_source == "MANUAL_INPUT":
                field_entry['truthSource'] = "MANUAL_INPUT"
                field_entry['explanation'] = "Manually overridden by human reviewer."
                field_entry['confidenceOverall'] = 1.0
                
                manual_value = decision.get('manualValue')
                manual_is_required = decision.get('manualIsRequired')
                manual_last_updated = decision.get('manualLastUpdated')

                field_entry['diff']['MANUAL_INPUT'] = {
                    "modified": True,
                    "value": manual_value,
                    "originalValue": manual_value, # For new manual input, originalValue is the manualValue
                    "lastUpdated": manual_last_updated,
                    "isRequired": manual_is_required,
                    "confidence": 1.0
                }
            else: # Human chose an existing source
                if chosen_source in field_entry['diff']:
                    field_entry['truthSource'] = chosen_source
                    field_entry['explanation'] = f"Overridden by human reviewer to use {chosen_source}."
                    field_entry['confidenceOverall'] = 1.0
                    
                    # Mark the chosen source as modified and update confidence
                    if isinstance(field_entry['diff'][chosen_source], dict):
                        field_entry['diff'][chosen_source]['modified'] = True
                        field_entry['diff'][chosen_source]['confidence'] = 1.0
                    # If it was ENUM.NO_FIELD, it cannot be marked as modified in the same way.
                    # The act of choosing it as truthSource is the override.
                    # If it needs to become a structured dict, that's a more complex edit.
                    # For now, if chosen_source points to a simple string (like ENUM.NO_FIELD),
                    # we just update top-level fields. The 'diff' entry remains a string.
                    # This case (choosing ENUM.NO_FIELD as truth) might need further design
                    # if we want to represent its "truthness" with a structured dict.
                    # However, current logic primarily focuses on choosing existing structured entries or adding new manual ones.

                else:
                    # Optional: Log a warning for invalid chosen_source if it's not MANUAL_INPUT
                    # print(f"Warning: Human decision for field '{field_name}' specified an invalid source '{chosen_source}'.")
                    pass # Skipping invalid source decision for now
    return evaluated_data
