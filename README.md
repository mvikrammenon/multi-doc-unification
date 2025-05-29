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
