import unittest
import os
import json
import csv
from unittest.mock import patch
from src.doc_reader import read_component_docs
from src.field_extractor import extract_fields_from_content
from src.field_aligner import align_and_normalize_fields
from src.field_comparer import compare_and_evaluate_fields
from src.report_generator import generate_csv_report
from src.human_reviewer import apply_human_decisions
from src.doc_generator import generate_unified_document
from src.utils import OutputMarkers

class TestStages(unittest.TestCase):

    def test_read_component_docs_existing_component(self):
        # Create dummy data for testing
        # Ensure data directory exists for the test
        os.makedirs("data/source1", exist_ok=True)
        os.makedirs("data/source2", exist_ok=True)
        os.makedirs("data/source3", exist_ok=True)
        
        # Use more realistic file content for doc_reader tests if it helps,
        # or simple placeholders if content doesn't matter for the test logic.
        s1_path = "data/source1/component1.txt"
        s2_path = "data/source2/component1.txt"
        s3_path = "data/source3/component1.txt"

        with open(s1_path, "w") as f: f.write("Doc for source1")
        with open(s2_path, "w") as f: f.write("Doc for source2")
        # Simulate source3 not having the component file for this specific test if needed,
        # or create it if it should exist. For this test, let's assume it exists.
        with open(s3_path, "w") as f: f.write("Doc for source3")

        component_docs = read_component_docs("component1")

        self.assertIn("source1", component_docs)
        self.assertIn("source2", component_docs)
        self.assertIn("source3", component_docs)
        self.assertEqual(component_docs["source1"], "Doc for source1")
        self.assertEqual(component_docs["source2"], "Doc for source2")
        self.assertEqual(component_docs["source3"], "Doc for source3")

        # Clean up
        os.remove(s1_path)
        os.remove(s2_path)
        os.remove(s3_path)
        # Potentially remove directories if they were created solely for this test
        # and if other tests don't rely on them.
        # For now, assume data/source* dirs are generally available from setup.

    def test_read_component_docs_non_existing_component(self):
        component_docs = read_component_docs("non_existent_component")
        self.assertEqual(len(component_docs), 0)

    @patch('crewai.Crew.kickoff')
    def test_extract_fields_from_content(self, mock_kickoff):
        sample_doc_content = """Field: Title
Value: Component One
Required: Yes
Last Updated: 2023-10-01

Field: Description
Value: This is the first component.
Required: Yes
Last Updated: 2023-10-05

Field: Version
Value: 1.0
Required: No
Last Updated: 2023-10-01"""

        expected_json_output_str = """
        [
            {
                "fieldName": "Title",
                "fieldValue": "Component One",
                "isRequired": true,
                "lastUpdated": "2023-10-01"
            },
            {
                "fieldName": "Description",
                "fieldValue": "This is the first component.",
                "isRequired": true,
                "lastUpdated": "2023-10-05"
            },
            {
                "fieldName": "Version",
                "fieldValue": "1.0",
                "isRequired": false,
                "lastUpdated": "2023-10-01"
            }
        ]
        """
        mock_kickoff.return_value = expected_json_output_str.strip()

        extracted_data = extract_fields_from_content(sample_doc_content)

        mock_kickoff.assert_called_once_with(inputs={'doc_content': sample_doc_content})
        
        self.assertIsInstance(extracted_data, list)
        self.assertEqual(len(extracted_data), 3)

        # Assertions for the first dictionary
        self.assertEqual(extracted_data[0]['fieldName'], "Title")
        self.assertEqual(extracted_data[0]['fieldValue'], "Component One")
        self.assertIsInstance(extracted_data[0]['isRequired'], bool)
        self.assertEqual(extracted_data[0]['isRequired'], True)
        self.assertEqual(extracted_data[0]['lastUpdated'], "2023-10-01")

        # Assertions for the second dictionary
        self.assertEqual(extracted_data[1]['fieldName'], "Description")
        self.assertEqual(extracted_data[1]['fieldValue'], "This is the first component.")
        self.assertIsInstance(extracted_data[1]['isRequired'], bool)
        self.assertEqual(extracted_data[1]['isRequired'], True)
        self.assertEqual(extracted_data[1]['lastUpdated'], "2023-10-05")

        # Assertions for the third dictionary
        self.assertEqual(extracted_data[2]['fieldName'], "Version")
        self.assertEqual(extracted_data[2]['fieldValue'], "1.0")
        self.assertIsInstance(extracted_data[2]['isRequired'], bool)
        self.assertEqual(extracted_data[2]['isRequired'], False)
        self.assertEqual(extracted_data[2]['lastUpdated'], "2023-10-01")

    @patch('crewai.Crew.kickoff')
    def test_align_and_normalize_fields(self, mock_kickoff):
        sample_extracted_data_by_source = {
            "source1": [
                {"fieldName": "Title", "fieldValue": "Component One", "isRequired": True, "lastUpdated": "2023-10-01"},
                {"fieldName": "Version", "fieldValue": "1.0", "isRequired": False, "lastUpdated": "2023-10-01"}
            ],
            "source2": [
                {"fieldName": "Title", "fieldValue": "Component 1", "isRequired": True, "lastUpdated": "2023-10-02"},
                {"fieldName": "Author", "fieldValue": "SourceTwo", "isRequired": False, "lastUpdated": "2023-10-02"}
            ],
            "source3": [ 
                {"fieldName": "Version", "fieldValue": "1.0.1", "isRequired": False, "lastUpdated": "2023-10-03"}
            ]
        }

        expected_json_output_str = """
        {
            "Title": {
                "source1": { "originalValue": "Component One", "lastUpdated": "2023-10-01", "isRequired": true },
                "source2": { "originalValue": "Component 1", "lastUpdated": "2023-10-02", "isRequired": true },
                "source3": "ENUM.NO_FIELD"
            },
            "Version": {
                "source1": { "originalValue": "1.0", "lastUpdated": "2023-10-01", "isRequired": false },
                "source2": "ENUM.NO_FIELD",
                "source3": { "originalValue": "1.0.1", "lastUpdated": "2023-10-03", "isRequired": false }
            },
            "Author": {
                "source1": "ENUM.NO_FIELD",
                "source2": { "originalValue": "SourceTwo", "lastUpdated": "2023-10-02", "isRequired": false },
                "source3": "ENUM.NO_FIELD"
            }
        }
        """
        mock_kickoff.return_value = expected_json_output_str.strip()

        aligned_data = align_and_normalize_fields(sample_extracted_data_by_source)

        mock_kickoff.assert_called_once_with(inputs={'extracted_data_by_source': sample_extracted_data_by_source})

        self.assertIsInstance(aligned_data, dict)
        self.assertIn("Title", aligned_data)
        self.assertIn("Version", aligned_data)
        self.assertIn("Author", aligned_data)

        # Assertions for "Title"
        self.assertIn("source1", aligned_data["Title"])
        self.assertEqual(aligned_data["Title"]["source1"]["originalValue"], "Component One")
        self.assertTrue(aligned_data["Title"]["source1"]["isRequired"])
        self.assertEqual(aligned_data["Title"]["source1"]["lastUpdated"], "2023-10-01")

        self.assertIn("source2", aligned_data["Title"])
        self.assertEqual(aligned_data["Title"]["source2"]["originalValue"], "Component 1")
        self.assertTrue(aligned_data["Title"]["source2"]["isRequired"])
        self.assertEqual(aligned_data["Title"]["source2"]["lastUpdated"], "2023-10-02")

        self.assertIn("source3", aligned_data["Title"])
        self.assertEqual(aligned_data["Title"]["source3"], str(OutputMarkers.NO_FIELD))

        # Assertions for "Version"
        self.assertIn("source1", aligned_data["Version"])
        self.assertEqual(aligned_data["Version"]["source1"]["originalValue"], "1.0")
        self.assertFalse(aligned_data["Version"]["source1"]["isRequired"])
        self.assertEqual(aligned_data["Version"]["source1"]["lastUpdated"], "2023-10-01")

        self.assertIn("source2", aligned_data["Version"])
        self.assertEqual(aligned_data["Version"]["source2"], str(OutputMarkers.NO_FIELD))

        self.assertIn("source3", aligned_data["Version"])
        self.assertEqual(aligned_data["Version"]["source3"]["originalValue"], "1.0.1")
        self.assertFalse(aligned_data["Version"]["source3"]["isRequired"])
        self.assertEqual(aligned_data["Version"]["source3"]["lastUpdated"], "2023-10-03")

        # Assertions for "Author"
        self.assertIn("source1", aligned_data["Author"])
        self.assertEqual(aligned_data["Author"]["source1"], str(OutputMarkers.NO_FIELD))

        self.assertIn("source2", aligned_data["Author"])
        self.assertEqual(aligned_data["Author"]["source2"]["originalValue"], "SourceTwo")
        self.assertFalse(aligned_data["Author"]["source2"]["isRequired"])
        self.assertEqual(aligned_data["Author"]["source2"]["lastUpdated"], "2023-10-02")

        self.assertIn("source3", aligned_data["Author"])
        self.assertEqual(aligned_data["Author"]["source3"], str(OutputMarkers.NO_FIELD))

    @patch('crewai.Crew.kickoff')
    def test_compare_and_evaluate_fields(self, mock_kickoff):
        sample_aligned_field_data = {
            "Title": {
                "source1": { "originalValue": "Component One", "lastUpdated": "2023-10-01", "isRequired": True },
                "source2": { "originalValue": "Component 1", "lastUpdated": "2023-10-02", "isRequired": True },
                "source3": str(OutputMarkers.NO_FIELD)
            },
            "Version": {
                "source1": { "originalValue": "1.0", "lastUpdated": "2023-10-01", "isRequired": False },
                "source2": str(OutputMarkers.NO_FIELD),
                "source3": { "originalValue": "1.0.1", "lastUpdated": "2023-10-03", "isRequired": False }
            }
        }

        expected_json_output_str = """
        {
            "Title": {
                "diff": {
                    "source1": { "modified": false, "value": "Component One", "originalValue": "Component One", "lastUpdated": "2023-10-01", "isRequired": true, "confidence": 0.85 },
                    "source2": { "modified": false, "value": "Component 1", "originalValue": "Component 1", "lastUpdated": "2023-10-02", "isRequired": true, "confidence": 0.9 },
                    "source3": { "modified": false, "value": "ENUM.NO_FIELD", "confidence": 0.5 }
                },
                "truthSource": "source2",
                "explanation": "Source2 chosen for Title due to more recent update and common value pattern.",
                "confidenceOverall": 0.9
            },
            "Version": {
                "diff": {
                    "source1": { "modified": false, "value": "1.0", "originalValue": "1.0", "lastUpdated": "2023-10-01", "isRequired": false, "confidence": 0.8 },
                    "source2": { "modified": false, "value": "ENUM.NO_FIELD", "confidence": 0.5 },
                    "source3": { "modified": false, "value": "1.0.1", "originalValue": "1.0.1", "lastUpdated": "2023-10-03", "isRequired": false, "confidence": 0.95 }
                },
                "truthSource": "source3",
                "explanation": "Source3 chosen for Version as it's the most recent and specific.",
                "confidenceOverall": 0.95
            }
        }
        """
        mock_kickoff.return_value = expected_json_output_str.strip()
        
        evaluated_data = compare_and_evaluate_fields(sample_aligned_field_data)

        mock_kickoff.assert_called_once_with(inputs={'aligned_field_data': sample_aligned_field_data})

        self.assertIsInstance(evaluated_data, dict)
        self.assertIn("Title", evaluated_data)
        self.assertIn("Version", evaluated_data)

        # Assertions for "Title"
        self.assertEqual(evaluated_data["Title"]["truthSource"], "source2")
        self.assertIn("explanation", evaluated_data["Title"])
        self.assertIsInstance(evaluated_data["Title"]["confidenceOverall"], float)
        self.assertEqual(evaluated_data["Title"]["diff"]["source1"]["value"], "Component One")
        self.assertIsInstance(evaluated_data["Title"]["diff"]["source1"]["confidence"], float)
        self.assertEqual(evaluated_data["Title"]["diff"]["source3"]["value"], str(OutputMarkers.NO_FIELD))
        self.assertFalse(evaluated_data["Title"]["diff"]["source1"]["modified"])
        self.assertTrue(evaluated_data["Title"]["diff"]["source1"]["isRequired"])
        self.assertEqual(evaluated_data["Title"]["diff"]["source1"]["originalValue"], "Component One")
        self.assertEqual(evaluated_data["Title"]["diff"]["source1"]["lastUpdated"], "2023-10-01")


        # Assertions for "Version"
        self.assertEqual(evaluated_data["Version"]["truthSource"], "source3")
        self.assertIn("explanation", evaluated_data["Version"])
        self.assertIsInstance(evaluated_data["Version"]["confidenceOverall"], float)
        self.assertEqual(evaluated_data["Version"]["diff"]["source1"]["value"], "1.0")
        self.assertIsInstance(evaluated_data["Version"]["diff"]["source1"]["confidence"], float)
        self.assertEqual(evaluated_data["Version"]["diff"]["source2"]["value"], str(OutputMarkers.NO_FIELD))
        self.assertFalse(evaluated_data["Version"]["diff"]["source3"]["modified"])
        self.assertFalse(evaluated_data["Version"]["diff"]["source3"]["isRequired"])
        self.assertEqual(evaluated_data["Version"]["diff"]["source3"]["originalValue"], "1.0.1")
        self.assertEqual(evaluated_data["Version"]["diff"]["source3"]["lastUpdated"], "2023-10-03")

    def test_generate_csv_report(self):
        sample_evaluated_data = {
            "Title": {
                "diff": {
                    "source1": { "modified": False, "value": "Component One", "originalValue": "Component One", "lastUpdated": "2023-10-01", "isRequired": True, "confidence": 0.85 },
                    "source2": { "modified": False, "value": "Component 1", "originalValue": "Component 1", "lastUpdated": "2023-10-02", "isRequired": True, "confidence": 0.9 },
                    "source3": { "modified": False, "value": str(OutputMarkers.NO_FIELD), "confidence": 0.5 }
                },
                "truthSource": "source2",
                "explanation": "Source2 chosen due to date.",
                "confidenceOverall": 0.90 
            },
            "Version": {
                "diff": {
                    "source1": { "modified": False, "value": "1.0", "originalValue": "1.0", "lastUpdated": "2023-10-01", "isRequired": False, "confidence": 0.7 },
                    "source2": { "modified": False, "value": str(OutputMarkers.NO_FIELD), "confidence": 0.5 },
                    "source3": { "modified": False, "value": "1.0.1", "originalValue": "1.0.1", "lastUpdated": "2023-10-03", "isRequired": False, "confidence": 0.8 }
                },
                "truthSource": "source3",
                "explanation": "Source3 chosen, but confidence is lower.",
                "confidenceOverall": 0.80
            },
            "Author": { 
                "diff": {
                    "source1": {"modified": False, "value": str(OutputMarkers.NO_FIELD), "confidence": 0.5},
                    "source2": {"modified": False, "value": str(OutputMarkers.NO_FIELD), "confidence": 0.5}
                },
                "truthSource": "NO_TRUTH_SOURCE_FOUND",
                "explanation": "All sources missing this field.",
                "confidenceOverall": 0.1 
            }
        }
        test_csv_path = "test_report.csv"
        generate_csv_report(sample_evaluated_data, test_csv_path)

        self.assertTrue(os.path.exists(test_csv_path))

        with open(test_csv_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            self.assertEqual(header, ["FieldName","TruthSource","TruthValue","TruthIsRequired","TruthLastUpdated","OverallConfidence","NeedsReview","AllSourcesDetailsJSON"])
            
            rows = list(reader)
            self.assertEqual(len(rows), 3)

            # Title Row
            title_row = rows[0]
            self.assertEqual(title_row[0], "Title")
            self.assertEqual(title_row[1], "source2")
            self.assertEqual(title_row[2], "Component 1")
            self.assertEqual(title_row[3], "True")
            self.assertEqual(title_row[4], "2023-10-02")
            self.assertEqual(title_row[5], "0.9")
            self.assertEqual(title_row[6], "False") # 0.9 is not < 0.9
            loaded_json_title = json.loads(title_row[7])
            self.assertEqual(loaded_json_title["source1"]["value"], "Component One")
            self.assertEqual(loaded_json_title["source3"]["value"], str(OutputMarkers.NO_FIELD))

            # Version Row
            version_row = rows[1]
            self.assertEqual(version_row[0], "Version")
            self.assertEqual(version_row[1], "source3")
            self.assertEqual(version_row[2], "1.0.1")
            self.assertEqual(version_row[3], "False")
            self.assertEqual(version_row[4], "2023-10-03")
            self.assertEqual(version_row[5], "0.8")
            self.assertEqual(version_row[6], "True") # 0.8 < 0.9

            # Author Row
            author_row = rows[2]
            self.assertEqual(author_row[0], "Author")
            self.assertEqual(author_row[1], "NO_TRUTH_SOURCE_FOUND")
            self.assertEqual(author_row[2], "N/A")
            self.assertEqual(author_row[3], "N/A")
            self.assertEqual(author_row[4], "N/A")
            self.assertEqual(author_row[5], "0.1")
            self.assertEqual(author_row[6], "True") # truthSource is NO_TRUTH_SOURCE_FOUND
        
        os.remove(test_csv_path)

    def test_apply_human_decisions(self):
        sample_evaluated_data = {
            "Version": {
                "diff": {
                    "source1": { "modified": False, "value": "1.0", "originalValue": "1.0", "lastUpdated": "2023-10-01", "isRequired": False, "confidence": 0.7 },
                    "source2": { "modified": False, "value": str(OutputMarkers.NO_FIELD), "confidence": 0.5 },
                    "source3": { "modified": False, "value": "1.0.1", "originalValue": "1.0.1", "lastUpdated": "2023-10-03", "isRequired": False, "confidence": 0.8 }
                },
                "truthSource": "source3",
                "explanation": "Source3 chosen, but confidence is lower.",
                "confidenceOverall": 0.80
            },
            "Description": {
                "diff": {
                    "source1": {"modified": False, "value": "Old Desc", "originalValue": "Old Desc", "lastUpdated": "2023-09-01", "isRequired": True, "confidence": 0.6}
                },
                "truthSource": "source1",
                "explanation": "Only source1 has this.",
                "confidenceOverall": 0.6
            }
        }

        # Test overriding with an existing source
        human_decisions_override_source = {
            "Version": {
                "chosenSource": "source1"
            }
        }
        # Deep copy for isolated testing
        data_for_override_test = json.loads(json.dumps(sample_evaluated_data))
        updated_data_override = apply_human_decisions(data_for_override_test, human_decisions_override_source)
        
        self.assertEqual(updated_data_override["Version"]["truthSource"], "source1")
        self.assertEqual(updated_data_override["Version"]["confidenceOverall"], 1.0)
        self.assertIn("Overridden by human reviewer to use source1", updated_data_override["Version"]["explanation"])
        self.assertTrue(updated_data_override["Version"]["diff"]["source1"].get("modified", False))
        self.assertEqual(updated_data_override["Version"]["diff"]["source1"]["confidence"], 1.0)

        # Test overriding with manual input
        human_decisions_manual_input = {
            "Description": {
                "chosenSource": "MANUAL_INPUT",
                "manualValue": "Brand new human-written description.",
                "manualIsRequired": True,
                "manualLastUpdated": "2024-01-10"
            }
        }
        # Deep copy for isolated testing
        data_for_manual_test = json.loads(json.dumps(sample_evaluated_data))
        updated_data_manual = apply_human_decisions(data_for_manual_test, human_decisions_manual_input)

        self.assertEqual(updated_data_manual["Description"]["truthSource"], "MANUAL_INPUT")
        self.assertEqual(updated_data_manual["Description"]["confidenceOverall"], 1.0)
        self.assertIn("Manually overridden", updated_data_manual["Description"]["explanation"])
        self.assertIn("MANUAL_INPUT", updated_data_manual["Description"]["diff"])
        manual_entry = updated_data_manual["Description"]["diff"]["MANUAL_INPUT"]
        self.assertEqual(manual_entry["value"], "Brand new human-written description.")
        self.assertTrue(manual_entry["isRequired"])
        self.assertEqual(manual_entry["lastUpdated"], "2024-01-10")
        self.assertEqual(manual_entry["confidence"], 1.0)
        self.assertTrue(manual_entry["modified"])

    def test_generate_unified_document(self):
        sample_final_data = {
            "Title": { # Standard field, source2 is truth
                "diff": {
                    "source1": { "modified": False, "value": "Old Title", "originalValue": "Old Title", "lastUpdated": "2023-09-01", "isRequired": True, "confidence": 0.8 },
                    "source2": { "modified": True, "value": "New Valid Title", "originalValue": "New Valid Title", "lastUpdated": "2023-10-10", "isRequired": True, "confidence": 1.0 }
                },
                "truthSource": "source2",
                "explanation": "Human chose source2.",
                "confidenceOverall": 1.0
            },
            "Version": { # Manually inputted field
                "diff": {
                    "MANUAL_INPUT": { "modified": True, "value": "2.0-beta", "originalValue": "2.0-beta", "lastUpdated": "2024-01-15", "isRequired": False, "confidence": 1.0 }
                },
                "truthSource": "MANUAL_INPUT",
                "explanation": "Manual input by human.",
                "confidenceOverall": 1.0
            },
            "ObsoleteField": { # Field where chosen truth is NO_FIELD
                "diff": {
                    "source1": { "modified": False, "value": str(OutputMarkers.NO_FIELD), "confidence": 1.0 },
                    "source2": { "modified": False, "value": "Data", "originalValue": "Data", "lastUpdated": "2023-01-01", "isRequired": True, "confidence": 0.5}
                },
                "truthSource": "source1", # Human confirmed this field is not applicable
                "explanation": "Human confirmed this field should be considered not present.",
                "confidenceOverall": 1.0
            },
            "LostField": { # Field with NO_TRUTH_SOURCE_FOUND
                    "diff": {
                    "source1": {"modified": False, "value": str(OutputMarkers.NO_FIELD), "confidence": 0.5},
                },
                "truthSource": "NO_TRUTH_SOURCE_FOUND",
                "explanation": "Cannot determine truth.",
                "confidenceOverall": 0.1
            }
        }
        test_doc_path = "test_unified_doc.txt"
        generate_unified_document(sample_final_data, test_doc_path)

        self.assertTrue(os.path.exists(test_doc_path))

        with open(test_doc_path, 'r') as f:
            content = f.read()
        
        expected_content = """Field: Title
Value: New Valid Title
Required: True
Last Updated: 2023-10-10

Field: Version
Value: 2.0-beta
Required: False
Last Updated: 2024-01-15

"""
        self.assertEqual(content, expected_content)
        os.remove(test_doc_path)

if __name__ == '__main__':
    unittest.main()
