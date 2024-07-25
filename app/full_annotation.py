import argparse
from categorization.llm_categorization import llm_invocation
from parsing.json_parsing import (
    convert_tsv_to_dict,
    process_parsed_output,
    update_json_file,
    tsv_to_json,
)


def main(file_path: str, json_file: str) -> None:
    columns_dict = convert_tsv_to_dict(file_path)

    tsv_to_json(file_path, json_file)

    # Create output for each column
    for key, value in columns_dict.items():
        print("Processing column:", key)
        try:
            # Invoke the chain with the input data
            input_dict = {key: value}
            print(key)
            # Column information is inserted in prompt template
            llm_response = llm_invocation(input_dict)

        except Exception as e:
            print("Error processing column:", key)
            print("Error message:", e)
            continue

        result = process_parsed_output(llm_response)  # type: ignore
        print(result)
        update_json_file(result, json_file, key)


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
