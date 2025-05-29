import json
from crewai import Agent, Task, Crew
from src.utils import OutputMarkers

# Define the CrewAI Agent
field_evaluator_agent = Agent(
    role="Field Comparison and Truth Analyst",
    goal="To analyze field data from multiple sources, identify discrepancies, assess the confidence of each piece of information, and determine the most likely 'true' value for each field, providing a rationale for the decision.",
    backstory="A highly analytical AI with a knack for sifting through conflicting information. It uses heuristics like 'last updated date', presence of keywords indicating verification, and general coherence to judge the reliability of data and select the best available version of each field.",
    allow_delegation=False,
    verbose=True
)

# Define the CrewAI Task
compare_fields_task = Task(
    description="""You will be given a Python dictionary named 'aligned_field_data' through the input variable `{inputs[aligned_field_data]}`.
This dictionary's keys are field names. The values are dictionaries where keys are source names (e.g., "source1") and values are either a dictionary `{'originalValue': ..., 'lastUpdated': ..., 'isRequired': ...}` or the string "ENUM.NO_FIELD".

Your goal is to process each field one by one and produce a comparison analysis. For each field:
1.  Analyze and compare the `originalValue`, `lastUpdated`, and `isRequired` status from all sources where the field is present.
2.  For each source entry for a field (including "ENUM.NO_FIELD" entries):
    *   Determine a `confidence` score (0.0 to 1.0) for the information from that source for that field. Consider `lastUpdated` (more recent might be better), `isRequired` (sometimes required fields are more scrutinized), and the `originalValue` itself (e.g., if it looks incomplete or placeholder). For "ENUM.NO_FIELD", the confidence might be lower, representing confidence that the field is indeed missing.
    *   The output `value` for this source should be its `originalValue` if present, or "ENUM.NO_FIELD" if not.
    *   The `modified` flag should be `false` at this stage (it's more for a later human review step, but we include it for schema consistency).
3.  Select a `truthSource`: the source name that provides the most reliable information for this field. If all sources are "ENUM.NO_FIELD", the `truthSource` can be null or a special marker like "NO_TRUTH_SOURCE_FOUND".
4.  Provide an `explanation`: a brief rationale for choosing the `truthSource`. This should mention factors like update recency, completeness, or other heuristics.
5.  Provide an `confidenceOverall` score (0.0 to 1.0) for the chosen `truthSource`'s value for this field.

The output structure for each field in the input `aligned_field_data` should be:
{
    "fieldName": { // This is the key in the output dictionary
        "diff": {
            "sourceName1": { "modified": false, "value": "...", "originalValue": "...", "lastUpdated": "...", "isRequired": true/false, "confidence": 0.0-1.0 },
            "sourceName2": { "modified": false, "value": "ENUM.NO_FIELD", "confidence": 0.0-1.0 }
            // ... and so on for all sources
        },
        "truthSource": "sourceName1", // or null / "NO_TRUTH_SOURCE_FOUND"
        "explanation": "Rationale here...",
        "confidenceOverall": 0.0-1.0
    }
}

Example input for `{inputs[aligned_field_data]}` (for a single field "Title"):
{
    "Title": {
        "source1": { "originalValue": "Component One", "lastUpdated": "2023-10-01", "isRequired": true },
        "source2": { "originalValue": "Component 1", "lastUpdated": "2023-10-02", "isRequired": true },
        "source3": "ENUM.NO_FIELD"
    }
}

Example JSON string output for this single field "Title":
"{
    \"Title\": {
        \"diff\": {
            \"source1\": { \"modified\": false, \"value\": \"Component One\", \"originalValue\": \"Component One\", \"lastUpdated\": \"2023-10-01\", \"isRequired\": true, \"confidence\": 0.8 },
            \"source2\": { \"modified\": false, \"value\": \"Component 1\", \"originalValue\": \"Component 1\", \"lastUpdated\": \"2023-10-02\", \"isRequired\": true, \"confidence\": 0.9 },
            \"source3\": { \"modified\": false, \"value\": \"ENUM.NO_FIELD\", \"confidence\": 0.5 }
        },
        \"truthSource\": \"source2\",
        \"explanation\": \"Source2 has a slightly more recent lastUpdated date for a similar value.\",
        \"confidenceOverall\": 0.9
    }
}"

Return the result for all processed fields STRICTLY as a JSON string, which is a dictionary where keys are field names.
""",
    expected_output="A valid JSON string. This string represents a dictionary where keys are field names. Each value is another dictionary containing 'diff' (detailing each source's data, confidence, and modified status), 'truthSource', 'explanation', and 'confidenceOverall'.",
    agent=field_evaluator_agent
)

def compare_and_evaluate_fields(aligned_field_data: dict) -> dict:
    """
    Compares and evaluates field data from multiple sources using a CrewAI agent.

    Args:
        aligned_field_data: A dictionary representing the aligned field data,
                            where keys are field names.

    Returns:
        A dictionary containing the comparison and evaluation results.
    """
    crew = Crew(
        agents=[field_evaluator_agent],
        tasks=[compare_fields_task],
        verbose=True
    )
    result_json_str = crew.kickoff(inputs={'aligned_field_data': aligned_field_data})

    if not isinstance(result_json_str, str):
        raise TypeError(f"Crew.kickoff() returned type {type(result_json_str)} instead of str. Content: {result_json_str}")

    evaluated_data = json.loads(result_json_str)
    return evaluated_data
