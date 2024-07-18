import argparse
import json
from typing import Dict, Any
from app.utils.llm_invocation import llm_invocation
from app.utils.process_llm_output import process_llm_output
from app.utils.file_operations.file_operations_factory import (
    FileOperationsFactory,
)


def main(file_path: str, json_file: str) -> None:
    file_op_factory: FileOperationsFactory = FileOperationsFactory()

    # Convert TSV to dictionary
    convert_op = file_op_factory.get_file_operation("convert_tsv_to_dict")()
    convert_op.execute(file_path)

    # Retrieve column strings from ConvertTSVToDict
    columns_dict: Dict[str, str] = convert_op.get_column_strings()  # type: ignore # noqa: E501

    # Convert TSV to JSON file
    tsv_to_json_op = file_op_factory.get_file_operation("tsv_to_json")()
    tsv_to_json_op.execute(file_path, json_file)

    # Create output for each column
    for key, value in columns_dict.items():
        print("Processing column:", key)
        try:
            # Invoke the LLM factories with the input data
            input_dict: Dict[str, Any] = {key: value}
            llm_response = llm_invocation(input_dict)
        except Exception as e:
            print("Error processing column:", key)
            print("Error message:", e)
            continue

        result = process_llm_output(llm_response)  # type: ignore
        print(result)

        # Check if result is a string or a TSVannotations object
        if isinstance(result, str):
            with open(json_file, "r+") as file:
                data: Dict[str, Any] = json.load(file)
                data[key] = result  # Update or add the key-value pair
                file.seek(0)  # Rewind to the start of the file
                json.dump(data, file, indent=4)  # Write the updated data
                file.truncate()  # Remove any remaining part of the old data
        else:
            update_op = file_op_factory.get_file_operation(
                "update_json_file"
            )()
            update_op.execute(result, json_file, key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process TSV file and update JSON output."
    )
    parser.add_argument("file_path", type=str, help="Path to the TSV file")
    parser.add_argument(
        "json_file", type=str, help="Path to the output JSON file"
    )

    args = parser.parse_args()

    main(args.file_path, args.json_file)
