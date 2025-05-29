import json
from crewai import Agent, Task, Crew
from src.utils import OutputMarkers

# Define the CrewAI Agent
field_normalizer_agent = Agent(
    role="Field Normalization Specialist",
    goal="To take lists of extracted fields from multiple documentation sources for the same component, identify all unique field names across these sources, and create a unified structure. For each unique field, indicate its value, last updated date, and required status from each source, or mark it as not existing in a particular source.",
    backstory="An meticulous AI assistant that excels at comparing structured data from different origins. It can create a comprehensive map of all fields, noting where each piece of information comes from and where information is missing.",
    allow_delegation=False,
    verbose=True
)

# Define the CrewAI Task
align_fields_task = Task(
    description="""You will be given a Python dictionary named 'extracted_data_by_source' through the input variable `{inputs[extracted_data_by_source]}`.
This dictionary's keys are source names (e.g., "source1", "source2"), and its values are lists of field dictionaries. Each field dictionary has "fieldName", "fieldValue", "isRequired", and "lastUpdated".

Your goal is to:
1. Collect all unique field names from all sources.
2. For each unique field name, create an entry in a result dictionary.
3. For each source, check if this unique field exists in that source's list of extracted fields.
   - If it exists, the value for that source under the unique field should be a dictionary:
     `{ "originalValue": "...", "lastUpdated": "...", "isRequired": true/false }`.
   - If it does not exist in a source, the value for that source under the unique field should be the string "ENUM.NO_FIELD".

Example input for `{inputs[extracted_data_by_source]}`:
{
    "source1": [
        {"fieldName": "Title", "fieldValue": "Component One", "isRequired": True, "lastUpdated": "2023-10-01"},
        {"fieldName": "Version", "fieldValue": "1.0", "isRequired": False, "lastUpdated": "2023-10-01"}
    ],
    "source2": [
        {"fieldName": "Title", "fieldValue": "Component 1", "isRequired": True, "lastUpdated": "2023-10-02"},
        {"fieldName": "Author", "fieldValue": "SourceTwo", "isRequired": False, "lastUpdated": "2023-10-02"}
    ]
}

Example JSON string output for this input:
"{
    \"Title\": {
        \"source1\": { \"originalValue\": \"Component One\", \"lastUpdated\": \"2023-10-01\", \"isRequired\": true },
        \"source2\": { \"originalValue\": \"Component 1\", \"lastUpdated\": \"2023-10-02\", \"isRequired\": true }
    },
    \"Version\": {
        \"source1\": { \"originalValue\": \"1.0\", \"lastUpdated\": \"2023-10-01\", \"isRequired\": false },
        \"source2\": \"ENUM.NO_FIELD\"
    },
    \"Author\": {
        \"source1\": \"ENUM.NO_FIELD\",
        \"source2\": { \"originalValue\": \"SourceTwo\", \"lastUpdated\": \"2023-10-02\", \"isRequired\": false }
    }
}"

Return this result STRICTLY as a JSON string.
""",
    expected_output="A valid JSON string representing a dictionary. Keys are unique field names. Values are dictionaries where keys are source names, and values are either a dictionary `{'originalValue': ..., 'lastUpdated': ..., 'isRequired': ...}` or the string 'ENUM.NO_FIELD'.",
    agent=field_normalizer_agent
)

def align_and_normalize_fields(extracted_data_by_source: dict[str, list[dict]]) -> dict:
    """
    Aligns and normalizes field data from multiple sources using a CrewAI agent.

    Args:
        extracted_data_by_source: A dictionary where keys are source names
                                  and values are lists of extracted field dictionaries.

    Returns:
        A dictionary representing the aligned and normalized field data.
    """
    crew = Crew(
        agents=[field_normalizer_agent],
        tasks=[align_fields_task],
        verbose=True 
    )
    result_json_str = crew.kickoff(inputs={'extracted_data_by_source': extracted_data_by_source})

    if not isinstance(result_json_str, str):
        raise TypeError(f"Crew.kickoff() returned type {type(result_json_str)} instead of str. Content: {result_json_str}")

    aligned_data = json.loads(result_json_str)
    return aligned_data
