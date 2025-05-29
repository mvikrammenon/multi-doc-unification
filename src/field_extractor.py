import json
import os
from crewai import Agent, Task, Crew

# Define the CrewAI Agent
doc_parser_agent = Agent(
    role="Documentation Field Extractor",
    goal="Extract structured field information (name, value, required status, last updated date) from documentation text. The input text will be provided in the 'doc_content' variable within the task's input dictionary.",
    backstory="An expert AI assistant specialized in parsing technical documentation and extracting key-value information along with metadata like 'required' status and 'last updated' dates. It understands various common documentation formats and expects input text via 'doc_content'.",
    allow_delegation=False,
    verbose=True
)

# Define the CrewAI Task
extract_fields_task = Task(
    description="""Analyze the documentation text provided in the input variable 'doc_content' which can be accessed via `{inputs[doc_content]}`.
Identify all distinct fields. For each field, extract the following information:
1. Field Name: The name of the field (e.g., "Title", "Description", "Version").
2. Field Value: The value associated with the field (e.g., "Component One", "1.0").
3. Required Status: Whether the field is marked as required or optional. Standardize this to a boolean (true for required, false for optional). Look for keywords like "Yes", "No", "True", "False", "Required", "Optional", and handle variations in casing.
4. Last Updated: The date the field was last updated (e.g., "2023-10-01").

The typical input text format is:
Field: [Field Name]
Value: [Field Value]
Required: [Yes/No/True/False/Required/Optional]
Last Updated: [YYYY-MM-DD]

Return the extracted information STRICTLY as a JSON string representation of a list of dictionaries. Each dictionary in the list represents a field and MUST have keys: "fieldName", "fieldValue", "isRequired" (boolean), and "lastUpdated".
Example of the JSON string to return:
"[
    {
        \"fieldName\": \"Title\",
        \"fieldValue\": \"Component One\",
        \"isRequired\": true,
        \"lastUpdated\": \"2023-10-01\"
    },
    {
        \"fieldName\": \"Description\",
        \"fieldValue\": \"This is the first component.\",
        \"isRequired\": true,
        \"lastUpdated\": \"2023-10-05\"
    }
]"
""",
    expected_output="A valid JSON string representing a list of dictionaries. Each dictionary must contain 'fieldName' (string), 'fieldValue' (string), 'isRequired' (boolean), and 'lastUpdated' (string 'YYYY-MM-DD'). For example: '[{\"fieldName\": \"Example Field\", \"fieldValue\": \"Example Value\", \"isRequired\": true, \"lastUpdated\": \"2024-01-01\"}]'.",
    agent=doc_parser_agent
)

def extract_fields_from_content(doc_content: str) -> list[dict]:
    """
    Extracts structured field information from documentation content using a CrewAI agent.

    Args:
        doc_content: The string content of the documentation.

    Returns:
        A list of dictionaries, where each dictionary represents a field
        and contains 'fieldName', 'fieldValue', 'isRequired', and 'lastUpdated'.
    """
    # It's good practice to ensure API keys are set if not using mocks,
    # though for this specific function with mocking, they aren't strictly used by the function's direct logic.
    # Example:
    # if "OPENAI_API_KEY" not in os.environ:
    #     raise ValueError("OPENAI_API_KEY environment variable not set.")

    crew = Crew(
        agents=[doc_parser_agent],
        tasks=[extract_fields_task],
        verbose=True # You can set verbose level for the crew execution
    )
    result_json_str = crew.kickoff(inputs={'doc_content': doc_content})
    
    # Ensure the result is a string before trying to load it as JSON
    if not isinstance(result_json_str, str):
        # This case might happen if the LLM returns a non-string output or if mocking is incorrect
        raise TypeError(f"Crew.kickoff() returned type {type(result_json_str)} instead of str. Content: {result_json_str}")

    extracted_data = json.loads(result_json_str)
    return extracted_data
